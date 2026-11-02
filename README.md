<!-- mcp-name: io.github.sepehr071/iran-jobs-mcp -->

<div align="center">

# iran-jobs-mcp: Iran jobs (استخدام) MCP server for AI agents, IranTalent + Jobinja + Jobvision

**iran-jobs-mcp is an unofficial, read-only MCP server that lets an AI agent search Iranian job ads, companies and pay on three job sites at once: IranTalent (ایران‌تلنت, irantalent.com), Jobinja (جابینجا, jobinja.ir) and Jobvision (جاب‌ویژن, jobvision.ir).**<br>
Its 37 tools search jobs on all three sites in one call, compare companies, employee reviews and interview reports, and compare pay for a role from IranTalent's salary survey and the pay in Jobinja and Jobvision ads.<br>
No API key or account is needed; it works in Claude, Cursor, Copilot and any other MCP client.

[![PyPI](https://img.shields.io/pypi/v/iran-jobs-mcp?color=2563eb)](https://pypi.org/project/iran-jobs-mcp/)
[![Python](https://img.shields.io/pypi/pyversions/iran-jobs-mcp)](https://pypi.org/project/iran-jobs-mcp/)
[![CI](https://github.com/sepehr071/iran-jobs-mcp/actions/workflows/ci.yml/badge.svg)](https://github.com/sepehr071/iran-jobs-mcp/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-16a34a)](https://github.com/sepehr071/iran-jobs-mcp/blob/main/LICENSE)

[For AI agents](#for-ai-agents) · [Quick start](#quick-start) · [Tools](#tools) · [Limits](#limits) · [فارسی](#فارسی)

</div>

---

## For AI agents

- **What:** unofficial MCP server (model context protocol) for irantalent.com, jobinja.ir and jobvision.ir, merged: job search, companies, top employers, market counts and pay from all three, plus each site's own tools.
- **Install:** `uvx iran-jobs-mcp` or `claude mcp add iran-jobs -- uvx iran-jobs-mcp`. Transport: stdio. Needs [uv](https://docs.astral.sh/uv/getting-started/installation/) (Python 3.10+).
- **Auth:** none. Optional `IRAN_JOBS_MCP_PROXY` (HTTP proxy URL, or a comma-separated list) applies to all three sites; system proxy settings are ignored.
- **Access:** read-only. It cannot log in, apply, post, save jobs or write reviews.
- **Tools:** 37, all prefixed `job_`. Five merged tools take `site` (`all` default, `irantalent`, `jobinja`, `jobvision`) and answer with one block per site; if one site fails its block holds an `error` and the others still answer. The other 32 are one site's own tools (`job_irantalent_*`, `job_jobinja_*`, `job_jobvision_*`).
- **Use when:** the user looks for jobs in Iran, asks what a company is like to work for, which employers are best rated, which fields hire most, or what a role pays.
- **Output:** compact JSON. Pay is Toman per month on IranTalent and Jobinja, million Toman per month on Jobvision. Text is mostly Persian.

## Quick start

You need [uv](https://docs.astral.sh/uv/getting-started/installation/). No API key or account.

Claude Code:

```bash
claude mcp add iran-jobs -- uvx iran-jobs-mcp
```

Claude Desktop, Cursor, VS Code and other clients:

```json
{
  "mcpServers": {
    "iran-jobs": { "command": "uvx", "args": ["iran-jobs-mcp"] }
  }
}
```

Example prompts:

- "Find remote Python jobs in Iran on all job sites."
- "Is Digikala a good employer? Show reviews and interview reports."
- "How much does a senior Java developer earn in Iran?"
- <span dir="rtl">آگهی‌های استخدام برنامه‌نویس پایتون در اصفهان را پیدا کن.</span>
- <span dir="rtl">حقوق حسابدار در تهران چقدر است؟</span>

## Tools

Merged (all three sites, `site` argument):

| Tool | What it does |
|---|---|
| `job_search` | Search job ads on IranTalent, Jobinja and Jobvision at once, one block of results per site. |
| `job_companies` | Find a company by name on IranTalent, Jobinja and Jobvision at once, one block per site. |
| `job_top_companies` | List each site's best-rated employers side by side: IranTalent top 50, Jobinja top 50, Jobvision top ranked. |
| `job_market` | Count open job ads per job category on IranTalent, Jobinja and Jobvision, one block per site. |
| `job_salary` | Compare monthly pay for a role from three sources: IranTalent's salary survey and the pay in Jobinja and Jobvision ads. |

IranTalent:

| Tool | What it does |
|---|---|
| `job_irantalent_search_jobs` | Search IranTalent job ads by keyword and filters (city, category, seniority, industry, employment, work type, company), newest first. |
| `job_irantalent_job` | Read one IranTalent job ad in full: description, requirements, salary, location, employer, view counts. |
| `job_irantalent_similar_jobs` | Find open jobs similar to one ad. |
| `job_irantalent_company` | Read a company profile: about text, industry, size, address, website, rating breakdown and newest open jobs. |
| `job_irantalent_company_reviews` | Read anonymous employee reviews of a company: ratings, pros, cons, reviewer's job title. |
| `job_irantalent_lookups` | List the valid filter slugs for `job_irantalent_search_jobs`. |
| `job_irantalent_job_market` | Count open jobs by category, industry, seniority, employment type, location or hiring company. |
| `job_irantalent_salary_reports` | List IranTalent salary reports: one per job specialty and seniority level. |
| `job_irantalent_salary` | Read the salary percentiles of one report, or of every seniority level of one specialty. |

Jobinja:

| Tool | What it does |
|---|---|
| `job_jobinja_search_jobs` | Search Jobinja job ads by keyword, province, city, category, remote, contract type, experience, benefits and minimum salary. |
| `job_jobinja_job` | Read one Jobinja job ad: salary, contract, experience, skills, degree and the full description. |
| `job_jobinja_company` | Read a company's Jobinja profile and its intro, culture and benefits text. |
| `job_jobinja_company_jobs` | List a company's open job ads, or its past (expired) ads. |
| `job_jobinja_search_companies` | Find companies by name, or browse one industry. |
| `job_jobinja_market` | Count open ads per job category, province, city, company industry and top skill. |
| `job_jobinja_skills` | Find skills matching a word, with how many ads ever listed each. |
| `job_jobinja_salary_stats` | Estimate monthly salaries for a kind of job from a sample of ad pages. |
| `job_jobinja_filters` | List every value the Jobinja search accepts. |

Jobvision:

| Tool | What it does |
|---|---|
| `job_jobvision_search` | Search Jobvision job ads with filters (city, category, seniority, experience, pay, remote, government sector, ...). |
| `job_jobvision_job` | Get the full text and requirements of one job ad. |
| `job_jobvision_similar_jobs` | List job ads Jobvision considers similar to one ad. |
| `job_jobvision_company` | Get an employer's profile and its currently open job ads. |
| `job_jobvision_companies` | Find companies by name or filters, best rated first. |
| `job_jobvision_interviews` | Get candidates' interview reports for a company: scores, difficulty, process and questions. |
| `job_jobvision_pay_stats` | Estimate pay for a role from the salaries open ads advertise. |
| `job_jobvision_careers` | Rank about 100 job titles in the career guide by satisfaction, median salary or open ads. |
| `job_jobvision_career` | Get the career-guide profile of one job title: salary distribution, demand, duties, skills, path. |
| `job_jobvision_market` | Count open ads per category, province, work type, seniority, experience, pay band or age. |
| `job_jobvision_suggest` | Autocomplete job titles the way Jobvision's search box does. |
| `job_jobvision_locations` | Find the province, city or Tehran area names the city filter accepts. |
| `job_jobvision_options` | List the values of one Jobvision filter. |
| `job_jobvision_government_news` | List public-sector recruitment announcements (banks, ministries, oil and gas...). |

## Limits

- Ids belong to one site: pass an id only to the tool of the site it came from.
- Most ads hide pay. Jobinja and Jobvision pay figures are what ads state, not what people earn; IranTalent's are its salary survey.
- `job_salary` makes about 25 requests and `job_market` about 80 (Jobvision counts each category separately); both are cached for two minutes.
- Jobinja answers only Iranian networks. From abroad set `IRAN_JOBS_MCP_PROXY` to a proxy that works, or run from Iran. The server ignores system proxy variables on purpose.
- Applying, saved jobs, the salary calculator and other account features are not covered.

## فارسی

<div dir="rtl">

iran-jobs-mcp یک سرور MCP غیررسمی و فقط‌خواندنی است که آگهی‌های استخدام، شرکت‌ها و حقوق را از سه سایت ایران‌تلنت، جابینجا و جاب‌ویژن هم‌زمان جست‌وجو می‌کند. نصب در Claude Code:

</div>

```bash
claude mcp add iran-jobs -- uvx iran-jobs-mcp
```

## Development

```bash
uv sync
uv run ruff check . && uv run ruff format --check .
uv run pytest -q          # offline tests on recorded fixtures
uv run pytest -m live -q  # live calls to the three sites
```

Releases: bump the version in `pyproject.toml` and `server.json`, run `uv lock`, then push a `v*` tag; GitHub Actions publishes to PyPI.

## Disclaimer

Unofficial and not affiliated with or endorsed by IranTalent, Jobinja or Jobvision. It is read-only and uses the public API and pages of those sites, which can change without notice.

## Author

Built and maintained by **Sepehr Radmard** (سپهر رادمرد). [LinkedIn](https://www.linkedin.com/in/sepehr-radmard) · [GitHub](https://github.com/sepehr071) · more servers in [iran-mcp](https://github.com/sepehr071/iran-mcp).

## License

[MIT](https://github.com/sepehr071/iran-jobs-mcp/blob/main/LICENSE)
