# ReasonOps ITSM CLI Reference

Comprehensive command-line interface for the ReasonOps ITSM framework, providing full access to all ITIL practices, AI agents, and management operations.

## 🚀 Quick Start

```bash
# Show version and framework info
python -m cli system version

# Initialize a new workspace
python -m cli system init --path ./my-workspace

# Check system status
python -m cli system status

# View dashboard
python -m cli dashboard

# Get help for any command
python -m cli <command> --help
```

## 📋 Command Categories

- [System Administration](#system-administration)
- [ITIL Practices](#itil-practices)
- [Configuration Management Database (CMDB)](#configuration-management-database-cmdb)
- [AI Agents](#ai-agents)
- [Service Level Management](#service-level-management)
- [Financial Management](#financial-management)
- [Data Operations](#data-operations)
- [Jobs & Automation](#jobs--automation)
- [Security Operations](#security-operations)
- [Metrics & Reporting](#metrics--reporting)
- [Knowledge Management](#knowledge-management)
- [Service Catalog](#service-catalog)
- [Workflow Management](#workflow-management)
- [Configuration Management](#configuration-management)
- [Testing & Validation](#testing--validation)
- [Import/Export](#importexport)

---

## System Administration

### `system version`
Show framework version and information.

```bash
python -m cli system version
```

### `system status`
Show system status and health of all components.

```bash
python -m cli system status [--json]
```

### `system init`
Initialize a new ReasonOps workspace.

```bash
python -m cli system init [--path PATH] [--force]
```

**Options:**
- `--path`: Directory to initialize (default: current directory)
- `--force`: Force initialization even if directory is not empty

---

## ITIL Practices

### Incident Management

#### `practices incident create`
Create a new incident.

```bash
python -m cli practices incident create \
  --title "Email server down" \
  --description "Email server is not responding" \
  --caller "john.doe@company.com" \
  --category "APPLICATION" \
  --impact high \
  --urgency high \
  [--json]
```

**Options:**
- `--title`: Incident title (required)
- `--description`: Detailed description
- `--caller`: Caller ID or email
- `--category`: Incident category
- `--impact`: Impact level (low, medium, high, critical)
- `--urgency`: Urgency level (low, medium, high, critical)

#### `practices incident list`
List incidents with optional filtering.

```bash
python -m cli practices incident list \
  [--status STATUS] \
  [--priority PRIORITY] \
  [--limit 20] \
  [--json]
```

#### `practices incident show`
Show detailed incident information.

```bash
python -m cli practices incident show INC001 [--json]
```

#### `practices incident update`
Update an existing incident.

```bash
python -m cli practices incident update INC001 \
  [--status STATUS] \
  [--priority PRIORITY] \
  [--assignee USER] \
  [--comment "Comment text"] \
  [--json]
```

### Problem Management

#### `practices problem create`
Create a new problem.

```bash
python -m cli practices problem create \
  --title "Recurring email delays" \
  --description "Users experiencing consistent email delays" \
  [--related-incidents INC001 INC002] \
  [--json]
```

#### `practices problem list`
List problems.

```bash
python -m cli practices problem list \
  [--status STATUS] \
  [--limit 20] \
  [--json]
```

### Change Management

#### `practices change create`
Create a new change request.

```bash
python -m cli practices change create \
  --title "Upgrade email server" \
  --description "Upgrade to latest version" \
  [--type normal|standard|emergency] \
  [--risk low|medium|high] \
  [--json]
```

#### `practices change list`
List change requests.

```bash
python -m cli practices change list \
  [--status STATUS] \
  [--type TYPE] \
  [--limit 20] \
  [--json]
```

---

## Configuration Management Database (CMDB)

### `cmdb add`
Add a configuration item.

```bash
python -m cli cmdb add \
  --name "PROD-WEB-01" \
  --type "Server" \
  [--class "Physical Server"] \
  [--status active] \
  [--location "Data Center 1"] \
  [--owner "IT Team"] \
  [--json]
```

### `cmdb list`
List configuration items.

```bash
python -m cli cmdb list \
  [--type TYPE] \
  [--status STATUS] \
  [--limit 20] \
  [--json]
```

### `cmdb show`
Show CI details.

```bash
python -m cli cmdb show CI_ID [--json]
```

### `cmdb relate`
Create a relationship between CIs.

```bash
python -m cli cmdb relate SOURCE_CI TARGET_CI \
  [--type depends_on] \
  [--json]
```

---

## AI Agents

### `agents orchestrator`
Run the integrated orchestrator demo.

```bash
python -m cli agents orchestrator
```

### `agents run`
Execute AI agent orchestration for an event.

```bash
python -m cli agents run \
  --event-type incident \
  --event-data '{"incident_id": "INC001", "severity": "high"}' \
  [--llm-config CONFIG_FILE] \
  [--json]
```

### `agents decisions`
List agent decision history.

```bash
python -m cli agents decisions \
  [--limit 50] \
  [--event-type EVENT_TYPE] \
  [--agent-name AGENT_NAME] \
  [--json]
```

### `agents configure`
Configure LLM provider for agents.

```bash
# Local Ollama setup
python -m cli agents configure \
  --provider ollama \
  --model llama2-7b \
  [--temperature 0.7] \
  [--json]

# OpenAI setup
python -m cli agents configure \
  --provider openai \
  --model gpt-4-turbo \
  --api-key "sk-..." \
  [--temperature 0.7] \
  [--json]
```

### `agents health`
Check health of LLM providers.

```bash
python -m cli agents health [--json]
```

### `agents providers`
List available LLM providers and models.

```bash
python -m cli agents providers [--json]
```

---

## Service Level Management

### `slm sync-availability`
Sync availability metrics into SLM.

```bash
python -m cli slm sync-availability [--json]
```

### `slm sync-outage-availability`
Sync outage-adjusted availability metrics.

```bash
python -m cli slm sync-outage-availability \
  [--days 30] \
  [--json]
```

### `slm feed-capacity-kpis`
Feed capacity KPIs (Response Time/Throughput) into SLM.

```bash
python -m cli slm feed-capacity-kpis [--json]
```

### `slm metrics`
Compute SLM metrics (availability, MTTR/MTBF, error budget).

```bash
python -m cli slm metrics \
  [--days 30] \
  [--json]
```

---

## Financial Management

### `financial penalties`
Apply supplier penalties for SLA breaches.

```bash
python -m cli financial penalties [--json]
```

### `financial chargeback`
Apply capacity-driven chargebacks.

```bash
python -m cli financial chargeback [--json]
```

### `financial budget show`
Show budget information.

```bash
python -m cli financial budget show \
  [--service SERVICE_NAME] \
  [--json]
```

---

## Data Operations

### `data export-monthly`
Export current month rollups.

```bash
python -m cli data export-monthly \
  [--out OUTPUT_FILE] \
  [--json]
```

### `data rollups`
Show rollups for a collection by month.

```bash
python -m cli data rollups \
  --collection penalties \
  [--fields amount penalty count] \
  [--group-by service agent_role] \
  [--month YYYY-MM] \
  [--json]
```

### `data clear`
Delete JSON data files under storage/data.

```bash
python -m cli data clear [--yes]
```

### `data backup`
Backup data to archive.

```bash
python -m cli data backup \
  [--path BACKUP_PATH] \
  [--compress]
```

### `data restore`
Restore data from backup.

```bash
python -m cli data restore \
  --path BACKUP_PATH \
  [--force]
```

---

## Jobs & Automation

### `jobs run`
Run periodic jobs.

```bash
python -m cli jobs run \
  [--iterations 1] \
  [--interval 10]
```

### `jobs list`
List available jobs.

```bash
python -m cli jobs list [--json]
```

---

## Security Operations

### `security simulate`
Simulate a security event.

```bash
python -m cli security simulate
```

### `security audit`
Run security audit.

```bash
python -m cli security audit \
  [--type access|config|data] \
  [--json]
```

---

## Metrics & Reporting

### `metrics show`
Show system metrics.

```bash
python -m cli metrics show \
  [--type incidents|problems|changes|availability|performance] \
  [--period day|week|month|quarter] \
  [--json]
```

### `dashboard`
Show integrated dashboard.

```bash
python -m cli dashboard [--json]
```

---

## Knowledge Management

### `knowledge create`
Create a knowledge article.

```bash
python -m cli knowledge create \
  --title "How to reset user password" \
  --content "Step-by-step instructions..." \
  [--category "How-To"] \
  [--tags password reset user] \
  [--json]
```

### `knowledge search`
Search knowledge articles.

```bash
python -m cli knowledge search "password reset" \
  [--limit 10] \
  [--json]
```

---

## Service Catalog

### `catalog list`
List service catalog items.

```bash
python -m cli catalog list \
  [--category CATEGORY] \
  [--json]
```

### `catalog add`
Add service catalog item.

```bash
python -m cli catalog add \
  --name "Email Account Setup" \
  [--description "Setup new email account"] \
  [--category "Account Management"] \
  [--price 25.00] \
  [--json]
```

---

## Workflow Management

### `workflow list`
List workflows.

```bash
python -m cli workflow list \
  [--status active|inactive] \
  [--json]
```

### `workflow execute`
Execute a workflow.

```bash
python -m cli workflow execute WF001 \
  [--params '{"param1": "value1"}'] \
  [--json]
```

---

## Configuration Management

### `config show`
Show configuration.

```bash
python -m cli config show \
  [--section SECTION] \
  [--json]
```

### `config set`
Set configuration value.

```bash
python -m cli config set api.timeout 30 [--json]
```

---

## Testing & Validation

### `test run`
Run tests.

```bash
python -m cli test run \
  [--suite SUITE_NAME] \
  [--verbose] \
  [--json]
```

### `test validate`
Validate system components.

```bash
python -m cli test validate \
  [--component storage|orchestrator|agents] \
  [--json]
```

---

## Import/Export

### `import`
Import data from file.

```bash
python -m cli import incidents.csv \
  [--type csv] \
  [--entity incidents] \
  [--dry-run] \
  [--json]
```

### `export`
Export data to file.

```bash
python -m cli export \
  --entity incidents \
  [--format json|csv|xml] \
  [--output incidents_backup.json] \
  [--filter '{"status": "open"}'] \
  [--json]
```

---

## Outage Management

### `outage record`
Record outage from open incidents.

```bash
python -m cli outage record [--minutes 10.0]
```

---

## 🎯 Common Usage Patterns

### Daily Operations

```bash
# Morning dashboard check
python -m cli dashboard

# Check agent health
python -m cli agents health

# View recent incidents
python -m cli practices incident list --limit 10

# Check system metrics
python -m cli metrics show --period day
```

### Incident Response

```bash
# Create high-priority incident
python -m cli practices incident create \
  --title "Production API down" \
  --impact critical \
  --urgency high

# Run AI agents for incident
python -m cli agents run \
  --event-type incident \
  --event-data '{"severity": "critical", "service": "api"}'

# Update incident status
python -m cli practices incident update INC001 \
  --status in_progress \
  --comment "Investigation started"
```

### System Maintenance

```bash
# Backup data
python -m cli data backup --compress

# Run system validation
python -m cli test validate

# Check security
python -m cli security audit

# Clear old data
python -m cli data clear --yes
```

### Reporting and Analytics

```bash
# Export monthly data
python -m cli data export-monthly --out reports/monthly.json

# Show detailed metrics
python -m cli metrics show --type incidents --period month

# Generate rollups
python -m cli data rollups --collection incidents --fields count
```

---

## 🔧 Configuration

### Environment Variables

- `DEBUG`: Enable debug mode for detailed error traces
- `REASONOPS_CONFIG`: Path to configuration file
- `REASONOPS_DATA_DIR`: Custom data directory path

### Global Options

Most commands support these global options:
- `--json`: Output in JSON format
- `--help`: Show command help

---

## 🎨 Output Formats

### Table Format (Default)
Human-readable tables for list commands.

### JSON Format
Machine-readable JSON output with `--json` flag.

```bash
python -m cli practices incident list --json | jq '.incidents[0]'
```

---

## 🔍 Troubleshooting

### Common Issues

1. **Command not found**: Make sure you're in the python-framework directory
2. **Permission errors**: Check file permissions for data directories
3. **LLM provider errors**: Verify API keys and provider availability
4. **Storage errors**: Ensure data directory exists and is writable

### Debug Mode

Enable debug mode for detailed error information:

```bash
DEBUG=1 python -m cli <command>
```

### Getting Help

```bash
# General help
python -m cli --help

# Category help
python -m cli practices --help

# Command help
python -m cli practices incident create --help
```

---

## 📚 Additional Resources

- [Framework Documentation](README.md)
- [AI Agents Guide](ai_agents/README.md)
- [ITIL Implementation Guide](docs/IMPLEMENTATION_SUMMARY.md)
- [Release Notes](docs/RELEASE_NOTES.md)

---

**Note**: This CLI provides comprehensive access to all ReasonOps ITSM framework capabilities. For the complete feature set, also see the Web UI at `http://localhost:5173` and REST API documentation.