"""Tools that ask IranTalent, Jobinja and Jobvision the same question and return the answers side by side."""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from typing import Annotated, Any, Literal

from mcp.server.mcpserver.exceptions import ToolError
from pydantic import Field

from .irantalent import salary as it_salary
from .irantalent import talent as it
from .jobinja import jobs as jj
from .jobvision import companies as jv_companies
from .jobvision import jobs as jv
from .jobvision import market as jv_market
from .registry import tool

SITE = Annotated[
    Literal["all", "irantalent", "jobinja", "jobvision"],
    Field(description="all (three side by side) or one site."),
]
Page = Annotated[int, Field(description="Page, 1-based, per site.", ge=1, le=500)]
SHAPE_ERRORS = (ToolError, KeyError, IndexError, TypeError, ValueError)


async def _each(site: str, **jobs: Callable[[], Awaitable[Any]]) -> dict[str, Any]:
    """Run the chosen sites at once. A failing site becomes {"error": ...}; all failing raises."""
    jobs = {n: f for n, f in jobs.items() if site in (n, "all")}
    results = await asyncio.gather(*(f() for f in jobs.values()), return_exceptions=True)
    out: dict[str, Any] = {}
    for name, r in zip(jobs, results, strict=True):
        if isinstance(r, SHAPE_ERRORS):
            out[name] = {"error": str(r) if isinstance(r, ToolError) else f"unexpected answer shape ({r!r})"}
        elif isinstance(r, BaseException):
            raise r
        else:
            out[name] = r
    if all("error" in v for v in out.values()):
        raise ToolError("; ".join(f"{n}: {v['error']}" for n, v in out.items()))
    return out


@tool("Search jobs on all sites")
async def job_search(
    keyword: Annotated[
        str | None,
        Field(description="Title/ad words, e.g. python, حسابدار.", max_length=100),
    ] = None,
    remote: Annotated[bool, Field(description="Remote only.")] = False,
    site: SITE = "all",
    page: Page = 1,
) -> dict[str, Any]:
    """Search job ads on IranTalent, Jobinja and Jobvision at once, one block of results per site.

    Ids are per site: use them only with that site's detail tool. For other filters use the site's own search tool.
    The same ad may appear on several sites.
    """
    kw = (keyword or "").strip() or None
    return await _each(
        site,
        irantalent=lambda: it.job_irantalent_search_jobs(keyword=kw, work_type="remote" if remote else None, page=page),
        jobinja=lambda: jj.job_jobinja_search_jobs(keyword=kw, remote=remote, page=page),
        jobvision=lambda: jv.job_jobvision_search(keyword=kw or "", remote=remote, page=page),
    )


@tool("Find companies on all sites")
async def job_companies(
    name: Annotated[str | None, Field(description="Company name, e.g. snapp.", max_length=60)] = None,
    site: SITE = "all",
    page: Page = 1,
) -> dict[str, Any]:
    """Find a company by name on IranTalent, Jobinja and Jobvision at once, one block per site.

    Gives each site's id: IranTalent `id` (UUID), Jobinja `slug`, Jobvision `id`. Browse by industry with
    job_jobinja_search_companies or job_jobvision_companies.
    """
    q = (name or "").strip() or None
    return await _each(
        site,
        irantalent=lambda: it.companies(search=q, page=page),
        jobinja=lambda: jj.job_jobinja_search_companies(keyword=q, page=page),
        jobvision=lambda: jv_companies.job_jobvision_companies(keyword=q or "", page=page),
    )


@tool("Best companies to work for")
async def job_top_companies(site: SITE = "all") -> dict[str, Any]:
    """List each site's best-rated employers side by side: IranTalent top 50, Jobinja top 50, Jobvision top ranked.

    Scales differ: IranTalent 1-5, Jobinja yearly score out of 10, Jobvision 1-5 with rank. Compare within one site.
    """
    return await _each(
        site,
        irantalent=it.top_companies,
        jobinja=jj.top_companies,
        jobvision=lambda: jv_companies.job_jobvision_companies(keyword=""),
    )


@tool("Job market by category on all sites")
async def job_market(site: SITE = "all") -> dict[str, Any]:
    """Count open job ads per job category on IranTalent, Jobinja and Jobvision, one block per site.

    Jobinja also counts per province, industry and skill. Other splits: job_irantalent_job_market,
    job_jobinja_market(province=...), job_jobvision_market.
    """
    return await _each(
        site,
        irantalent=lambda: it.job_irantalent_job_market(breakdown="categories"),
        jobinja=jj.job_jobinja_market,
        jobvision=lambda: jv_market.job_jobvision_market(by="category"),
    )


@tool("Salary for a role on all sites")
async def job_salary(
    role: Annotated[str, Field(description="Job title or skill, e.g. python.", min_length=1, max_length=60)],
    site: SITE = "all",
) -> dict[str, Any]:
    """Compare monthly pay for a role from three sources: IranTalent's salary survey and the pay in Jobinja and Jobvision ads.

    IranTalent: survey percentiles (net Toman) plus other matching report slugs. Jobinja: stated minimums of ad sample
    (Toman). Jobvision: median/quartiles of advertised ranges (million Toman). Different measures; cite each. Slow: ~25 requests.
    """
    r = role.strip()

    async def irantalent() -> dict[str, Any]:
        found = await it_salary.job_irantalent_salary_reports(search=r)
        if not found["reports"]:
            raise ToolError(f"No IranTalent salary report matches '{r}'. Try job_irantalent_salary_reports.")
        first, *more = found["reports"]
        return {
            **await it_salary.job_irantalent_salary(report=first["slug"]),
            "other_reports": [x["slug"] for x in more[:10]],
        }

    return await _each(
        site,
        irantalent=irantalent,
        jobinja=lambda: jj.job_jobinja_salary_stats(keyword=r),
        jobvision=lambda: jv.job_jobvision_pay_stats(keyword=r),
    )
