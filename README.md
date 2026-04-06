# skyportal-mcp

MCP ([Model Context Protocol](https://modelcontextprotocol.io)) server for [SkyPortal](https://skyportal.io) and [Fritz](https://fritz.science). Query astronomical transient data — photometry, spectra, classifications, observability — directly from AI coding assistants like Claude Code, Claude Desktop, and Cursor.

You do **not** need a local SkyPortal deployment. Point this server at any SkyPortal/Fritz URL and authenticate with your API token.

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

### HTTP mode (multi-user)

For shared deployments where multiple users connect with their own tokens:

```bash
MCP_TRANSPORT=http MCP_PORT=8000 SKYPORTAL_URL="https://fritz.science" python -m skyportal_mcp
```

Clients connect to `http://localhost:8000/mcp` and pass their SkyPortal API token as a Bearer header.

## Available Tools

### Source Data — `source_products.py`
| Tool | Description |
|------|-------------|
| `get_source_photometry` | Light curve data as CSV (mag or flux format) |
| `get_source_spectra` | Spectroscopic observations (summary, CSV, or JSON) |
| `get_source_classifications` | Classification history with probabilities |
| `get_source_comments_and_annotations` | User comments and ML annotations |
| `get_source_host_galaxy` | Host galaxy properties and offset |
| `get_tns_summary` | Complete TNS/AstroNote report in one call |

### Analysis — `analysis.py`
| Tool | Description |
|------|-------------|
| `analyze_light_curve` | Rise/fade times, peak brightness, multi-band analysis |
| `analyze_color_evolution` | Color curves (g-r) with matched and interpolated methods |

### Observing — `observing.py`, `astro_utils.py`
| Tool | Description |
|------|-------------|
| `get_source_observability` | Observing windows from Keck, VLT, Gemini, Palomar, etc. |
| `convert_time` | MJD / JD / ISO / Unix time conversion |
| `get_survey_urls` | Links to Legacy Survey, PanSTARRS, SDSS, NED, SIMBAD, etc. |
| `search_sources_near_position` | Cone search in SkyPortal |

### API Access — `api.py`
| Tool | Description |
|------|-------------|
| `call_skyportal_api` | Direct API calls to any SkyPortal endpoint |
| `get_api_quick_reference` | API endpoint documentation |
| `get_tools_quick_reference` | Tool usage guide |

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

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SKYPORTAL_URL` | `http://localhost:5001` | SkyPortal/Fritz instance URL |
| `SKYPORTAL_TOKEN` | (none) | API token for authentication |
| `MCP_TRANSPORT` | `stdio` | Transport mode: `stdio` or `http` |
| `MCP_HOST` | `127.0.0.1` | HTTP mode bind address |
| `MCP_PORT` | `8000` | HTTP mode port |
| `MCP_BASE_URL` | `http://localhost:{MCP_PORT}` | Public URL for OAuth callbacks (HTTP mode) |

## License

BSD 3-Clause
