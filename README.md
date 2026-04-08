# skyportal-mcp

> **Beta:** This project is under active development. Bug reports, feature requests, and pull requests are very welcome — please [open an issue](https://github.com/AnastasiaKWei/skyportal-mcp/issues) or submit a PR.

A **local** MCP ([Model Context Protocol](https://modelcontextprotocol.io)) server for [SkyPortal](https://skyportal.io) and [Fritz](https://fritz.science). It runs on your own machine and exposes SkyPortal data as tools that AI coding assistants — Claude Code, Claude Desktop, Cursor — can call directly. Query astronomical transient data — photometry, spectra, classifications, observability — without leaving your AI assistant.

> **Compatibility:** This has been tested with **Claude Code** and **Claude Desktop**. It has **not** been tested with other MCP-compatible clients (e.g., Cursor, OpenAI Codex, Gemini, or other services) — the setup steps for those clients may differ from the instructions below.

## Installation

```bash
git clone https://github.com/AnastasiaKWei/skyportal-mcp.git
cd skyportal-mcp
pip install -e .
```

## Configuration

Set two environment variables:

```bash
export SKYPORTAL_URL="https://fritz.science"    # Your SkyPortal/Fritz instance
export SKYPORTAL_TOKEN="your-api-token-here"    # From your profile page
```

For Fritz, get your token at https://fritz.science/profile — click your username, scroll to **API Token**, and copy it.

### Claude Code

Add to your Claude Code MCP config (`~/.claude.json`):

```json
{
  "mcpServers": {
    "skyportal": {
      "command": "python",
      "args": ["-m", "skyportal_mcp"],
      "env": {
        "SKYPORTAL_URL": "https://fritz.science",
        "SKYPORTAL_TOKEN": "your-token"
      }
    }
  }
}
```

### Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS):

```json
{
  "mcpServers": {
    "skyportal": {
      "command": "python",
      "args": ["-m", "skyportal_mcp"],
      "env": {
        "SKYPORTAL_URL": "https://fritz.science",
        "SKYPORTAL_TOKEN": "your-token"
      }
    }
  }
}
```

### Cursor

Add to `.cursor/mcp.json` in your project root:

```json
{
  "mcpServers": {
    "skyportal": {
      "command": "python",
      "args": ["-m", "skyportal_mcp"],
      "env": {
        "SKYPORTAL_URL": "https://fritz.science",
        "SKYPORTAL_TOKEN": "your-token"
      }
    }
  }
}
```

## Available Tools

> **Read vs Write**
> - **Read** — queries data from SkyPortal/Fritz; no data is created or modified.
> - **Write (SkyPortal)** — can create, update, or delete data in your SkyPortal/Fritz account. Use with care; these operations may not be reversible.
> - **Write (local)** — creates files on your local machine (notebooks, CSVs). Does not touch SkyPortal.

### Source Data — `source_products.py`
| Tool | Mode | Description |
|------|------|-------------|
| `get_source_photometry` | Read | Light curve data as CSV (mag or flux format) |
| `get_source_spectra` | Read | Spectroscopic observations (summary, CSV, or JSON) |
| `get_source_classifications` | Read | Classification history with probabilities |
| `get_source_comments_and_annotations` | Read | User comments and ML annotations |
| `get_source_host_galaxy` | Read | Host galaxy properties and offset |
| `get_tns_summary` | Read | Complete TNS/AstroNote report in one call |

### Analysis — `analysis.py`
| Tool | Mode | Description |
|------|------|-------------|
| `analyze_light_curve` | Read / Write (local) | Rise/fade times, peak brightness; notebook mode writes `.ipynb` + CSV to disk |
| `analyze_color_evolution` | Read / Write (local) | Color curves (g-r); notebook mode writes `.ipynb` + CSV to disk |

### Observing — `observing.py`, `astro_utils.py`
| Tool | Mode | Description |
|------|------|-------------|
| `get_source_observability` | Read | Observing windows from Keck, VLT, Gemini, Palomar, etc. |
| `convert_time` | Read | MJD / JD / ISO / Unix time conversion |
| `get_survey_urls` | Read | Links to Legacy Survey, PanSTARRS, SDSS, NED, SIMBAD, etc. |
| `search_sources_near_position` | Read | Cone search in SkyPortal |

### Filtering — `filtering.py`
| Tool | Mode | Description |
|------|------|-------------|
| `filter_candidates` | Read | Search the scanning page for candidates matching criteria |
| `get_candidate_filter_reference` | Read | Documentation for available filter parameters |
| `generate_watchlist_filter` | Read | Generate MongoDB pipeline JSON for a watchlist (output only, not saved to Fritz) |

### Bulk Analysis — `bulk_analysis.py`
| Tool | Mode | Description |
|------|------|-------------|
| `generate_bulk_lightcurve_code` | Write (local) | Writes a Jupyter notebook to `ztf_lightcurves/` for bulk ZTF light curve downloads |
| `generate_cone_search_code` | Write (local) | Writes code to `ztf_cone_search/` for multi-position cone searches |
| `generate_fritz_bulk_query_code` | Write (local) | Writes a notebook to `fritz_data/` for bulk Fritz photometry/spectra downloads |
| `generate_alert_download_code` | Write (local) | Writes a notebook to `ztf_alerts/` for downloading ZTF alert packets |
| `generate_field_visualization_code` | Write (local) | Writes code to visualize ZTF field and CCD coverage |

### API Access — `api.py`
| Tool | Mode | Description |
|------|------|-------------|
| `call_skyportal_api` | Read / ⚠️ Write (SkyPortal) | Direct API calls to any endpoint — **POST/PUT/DELETE will modify your SkyPortal account** |
| `get_api_quick_reference` | Read | API endpoint documentation |
| `get_tools_quick_reference` | Read | Tool usage guide |




## Test Prompts

Try these prompts after connecting to verify the tools work. Replace source names with ones you have access to on your SkyPortal instance.

### Source Data

**Photometry:**
> "Get the g and r band photometry for ZTF20acigmel"

Expects: CSV table with MJD, filter, mag, magerr columns. Should return both ztfg and ztfr data points.

**Spectra:**
> "Show me the spectra for ZTF20acigmel"

Expects: Summary listing each spectrum with date, instrument, wavelength range, and a Fritz link.

**Classifications:**
> "What are the classifications for ZTF20acigmel?"

Expects: List of classifications with type (e.g., SN Ia), probability, classifier name, and date.

**Comments and annotations:**
> "Show me the comments and ML annotations for ZTF20acigmel"

Expects: User comments with text/author/date, plus annotation key-value pairs (e.g., braai score, cross-match results).

**Host galaxy:**
> "What is the host galaxy of ZTF20acigmel?"

Expects: Galaxy name, coordinates, redshift, distance, stellar mass, and angular offset from the transient.

**TNS summary:**
> "Generate a TNS report for ZTF20acigmel"

Expects: Formatted report with coordinates (deg + HMS/DMS), discovery info, photometry summary, classification, spectroscopy, and host galaxy — ready to paste into a TNS submission.

### Analysis

**Light curve analysis (text):**
> "Analyze the light curve of ZTF20acigmel in g and r bands. Give me a text summary."

Expects: Per-band summary with peak magnitude, peak date, rise time, fade time, and duration.

**Light curve analysis (notebook):**
> "Analyze the light curve of ZTF20acigmel and generate a notebook"

Expects: Creates a Jupyter notebook with interactive Plotly light curve plots and editable analysis code cells.

**Color evolution (text):**
> "What is the g-r color evolution of ZTF20acigmel? Text summary please."

Expects: Color at peak, color trend (bluing/reddening/stable), and a table of color measurements over time.

### Observing

**Observability:**
> "When can I observe ZTF20acigmel from Keck and Palomar tonight?"

Expects: Per-telescope observing windows with rise/set times (UTC and local), transit time, peak altitude, and airmass.

**Time conversion:**
> "Convert MJD 60000 to a calendar date"

Expects: All formats — MJD, JD, ISO datetime, and Unix timestamp.

**Survey links:**
> "Get survey links for RA=150.0, Dec=2.0"

Expects: Clickable URLs for Legacy Survey, PanSTARRS, SDSS, NED, SIMBAD, VizieR, WISE, DSS, and others.

**Cone search:**
> "Search for sources within 10 arcsec of RA=150.0, Dec=2.0"

Expects: List of sources sorted by separation, with source ID, coordinates, separation in arcsec, and saved groups.

### API Access

**Direct API call:**
> "Use the SkyPortal API to get the source page for ZTF20acigmel"

Expects: Raw JSON response from `/api/sources/ZTF20acigmel`.

### Multi-Tool Prompts

These prompts exercise multiple tools in sequence, testing the AI assistant's ability to chain tool calls.

**Photometry + classification + observability:**
> "Get the photometry and classification for ZTF20acigmel, then check if it's observable from Keck tonight"

Expects: The assistant calls `get_source_photometry`, `get_source_classifications`, and `get_source_observability` (either in parallel or sequentially), then synthesizes the results.

**Cone search + photometry:**
> "Search for sources within 5 arcsec of RA=210.9, Dec=54.3 and get the photometry for any matches"

Expects: First calls `search_sources_near_position`, then calls `get_source_photometry` for each result.

**TNS report + observability:**
> "Generate a TNS summary for ZTF20acigmel and tell me when I can observe it from VLT"

Expects: Calls `get_tns_summary` and `get_source_observability` (potentially in parallel), then presents both results.

**Light curve analysis + color evolution:**
> "Analyze both the light curve and color evolution of ZTF20acigmel in text format"

Expects: Calls `analyze_light_curve` and `analyze_color_evolution`, presenting rise/fade metrics alongside color trend information.

## License

BSD 3-Clause
