import json

import httpx
import pytest

from iran_jobs_mcp.irantalent import http as it_http
from iran_jobs_mcp.jobinja import http as jj_http
from iran_jobs_mcp.jobvision import http as jv_http

pytestmark = pytest.mark.anyio

MERGED = {"job_search", "job_companies", "job_top_companies", "job_market", "job_salary"}
IT_SEARCH = "/api/v1/employer/position/search-by-slug"
JV_LIST = "/api/v1/JobPost/List"


async def test_tool_list(client):
    tools = {t.name: t for t in (await client.list_tools()).tools}
    assert len(tools) == 37 and MERGED <= set(tools)
    assert all(n in MERGED or n.startswith(("job_irantalent_", "job_jobinja_", "job_jobvision_")) for n in tools)
    for t in tools.values():
        assert t.annotations.read_only_hint is True, t.name
        assert t.description.splitlines()[0].endswith("."), t.name
    assert all("site" in tools[n].input_schema["properties"] for n in MERGED)


def test_one_proxy_variable_feeds_all_clients(monkeypatch):
    monkeypatch.setenv("IRAN_JOBS_MCP_PROXY", "http://127.0.0.1:1, http://127.0.0.1:2")
    monkeypatch.setenv("JOBINJA_MCP_PROXY", "http://old:1")
    assert (
        it_http._proxies() == jj_http._proxies() == jv_http._proxies() == ["http://127.0.0.1:1", "http://127.0.0.1:2"]
    )


async def test_search_all_sites_with_remote(client, web):
    web[IT_SEARCH] = "search.json"
    web["/jobs"] = "search.html"
    web[JV_LIST] = "list.json"
    r = (await client.call_tool("job_search", {"keyword": "python", "remote": True})).structured_content
    assert set(r) == {"irantalent", "jobinja", "jobvision"}
    assert r["irantalent"]["jobs"] and r["jobinja"]["jobs"] and r["jobvision"]["jobs"]
    by_path = {c.url.path: c for c in web.calls}
    assert json.loads(by_path[IT_SEARCH].content) == {"page": 1, "keyword": "python", "work_type": "remote"}
    assert by_path["/jobs"].url.params["filters[remote]"] == "1"
    jv = json.loads(by_path[JV_LIST].content)
    assert jv["keyword"] == "python" and jv["isRemote"] is True


async def test_one_site_failing_leaves_the_others(client, web):
    web[IT_SEARCH] = "search.json"
    web["/jobs"] = lambda req: httpx.Response(403, text="Access Denied")
    web[JV_LIST] = "list.json"
    r = (await client.call_tool("job_search", {"keyword": "python"})).structured_content
    assert "Iranian" in r["jobinja"]["error"] and r["irantalent"]["jobs"] and r["jobvision"]["jobs"]


async def test_all_sites_failing_is_an_error(client, web):
    r = await client.call_tool("job_top_companies", {})
    assert r.is_error and all(s in r.content[0].text for s in ("irantalent:", "jobinja:", "jobvision:"))


async def test_site_picks_one(client, web):
    web["/top50"] = "top50.html"
    r = (await client.call_tool("job_top_companies", {"site": "jobinja"})).structured_content
    assert set(r) == {"jobinja"} and r["jobinja"]["companies"][0]["slug"] == "rirais"
    assert {c.url.path for c in web.calls} == {"/top50"}


async def test_top_companies_side_by_side(client, web):
    web["/api/v1/candidate/brand/best-companies"] = "best.json"
    web["/top50"] = "top50.html"
    web["/api/v1/Company/GetListOfFilteredCompaniesSummaries"] = "companies.json"
    r = (await client.call_tool("job_top_companies", {})).structured_content
    assert all(r[s]["companies"] for s in ("irantalent", "jobinja", "jobvision"))


async def test_companies_by_name(client, web):
    web["/api/v1/candidate/brand"] = "brands.json"
    web["/companies"] = "companies.html"
    web["/api/v1/Company/GetListOfFilteredCompaniesSummaries"] = "companies.json"
    r = (await client.call_tool("job_companies", {"name": "snapp"})).structured_content
    assert all(r[s]["companies"] for s in ("irantalent", "jobinja", "jobvision"))
    by_path = {c.url.path: c for c in web.calls}
    assert by_path["/api/v1/candidate/brand"].url.params["search"] == "snapp"
    assert by_path["/companies"].url.params["keyword"] == "snapp"
    assert json.loads(by_path["/api/v1/Company/GetListOfFilteredCompaniesSummaries"].content)["keyword"] == "snapp"


async def test_salary_irantalent_reads_first_matching_report(client, web):
    web["/wp-json/wp/v2/salary-specialty"] = "wp_specialty.json"
    web["/wp-json/wp/v2/salary-seniority"] = "wp_seniority.json"
    web["/wp-json/wp/v2/salary-report"] = "wp_reports.json"
    web["/salary-report/java-senior-salary/"] = "salary_report.html"
    r = (await client.call_tool("job_salary", {"role": "java-senior", "site": "irantalent"})).structured_content
    assert r["irantalent"]["monthly_net_toman_by_persian_year"]
    r = await client.call_tool("job_salary", {"role": "no-such-role-xyz", "site": "irantalent"})
    assert r.is_error and "No IranTalent salary report" in r.content[0].text


@pytest.mark.live
@pytest.mark.parametrize("tool,args", [("job_search", {"keyword": "python"}), ("job_salary", {"role": "java"})])
async def test_live_merged_answers_from_every_site(client, tool, args):
    r = (await client.call_tool(tool, args)).structured_content
    assert set(r) == {"irantalent", "jobinja", "jobvision"}
    assert not [s for s, v in r.items() if "error" in v], r


@pytest.mark.live
async def test_live_market_and_companies(client):
    m = (await client.call_tool("job_market", {})).structured_content
    assert m["irantalent"]["items"] and m["jobinja"]["categories"] and "error" not in m["jobvision"]
    c = (await client.call_tool("job_companies", {"name": "digikala"})).structured_content
    assert all(c[s]["companies"] for s in ("irantalent", "jobinja", "jobvision")), c
