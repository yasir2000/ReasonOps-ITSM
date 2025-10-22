# Incident Management Practice

## Purpose

To minimize the negative impact of incidents by restoring normal service operation as quickly as possible.

## Description

An **incident** is an unplanned interruption to a service or reduction in the quality of a service. Incident management ensures that normal service operation is restored as quickly as possible with the least possible impact on business operations.

## Key Concepts

### What is an Incident?
- Unplanned interruption to service
- Reduction in quality of service
- Failure of configuration item (CI) that has not yet impacted service

### Incident vs. Problem
- **Incident**: Focus on restoring service quickly
- **Problem**: Focus on finding and fixing root cause

### Major Incidents
- High-impact incidents requiring special handling
- Separate procedures and escalation paths
- Executive communication requirements

## Process Flow

```
Incident         Incident          Incident         Incident        Incident
Detection   →    Logging      →    Categorization → Prioritization → Investigation
    ↓               ↓                    ↓               ↓               ↓
User Report    Service Desk      Category/          Priority         Diagnosis &
Monitoring     Single Point      Subcategory        Matrix           Resolution
Alerts         of Contact        Assignment         P1-P4            Actions
```

```
Incident         Incident          Incident         Service
Resolution  →    Recovery     →    Closure     →    Restoration
    ↓               ↓                ↓               ↓
Implement       Verify Service    Document        Normal Service
Solution        Restoration       Resolution      Operation
```

## Roles and Responsibilities

### Service Desk
- **Primary Role**: First point of contact for incident reporting
- **Responsibilities**:
  - Log all incidents
  - Provide initial classification and prioritization
  - Attempt first-line resolution
  - Escalate when necessary
  - Keep users informed of progress

### Incident Manager
- **Primary Role**: Overall incident lifecycle management
- **Responsibilities**:
  - Monitor incident resolution progress
  - Manage escalations
  - Coordinate with technical teams
  - Ensure incidents are resolved within SLA
  - Report on incident metrics

### Technical Support Teams (L2/L3)
- **Primary Role**: Technical investigation and resolution
- **Responsibilities**:
  - Investigate complex incidents
  - Implement technical solutions
  - Provide expertise for resolution
  - Document technical details
  - Support knowledge transfer

### Major Incident Manager
- **Primary Role**: Coordinate major incident response
- **Responsibilities**:
  - Lead major incident bridge calls
  - Coordinate technical teams
  - Manage stakeholder communication
  - Ensure business continuity measures
  - Conduct post-incident reviews

## Incident Classification

### Categorization
Groups incidents by type for analysis and routing:

**Hardware Categories:**
- Server hardware
- Network hardware
- Desktop/laptop hardware
- Storage systems
- Security hardware

**Software Categories:**
- Operating systems
- Applications
- Databases
- Middleware
- Security software

**Service Categories:**
- Email services
- Web services
- Network services
- Telephony services
- Security services

### Priority Matrix

| **Impact** | **Urgency** | **Priority** | **Resolution Target** |
|------------|-------------|--------------|----------------------|
| High | High | P1 (Critical) | 1 hour |
| High | Medium | P2 (High) | 4 hours |
| High | Low | P3 (Medium) | 8 hours |
| Medium | High | P2 (High) | 4 hours |
| Medium | Medium | P3 (Medium) | 8 hours |
| Medium | Low | P4 (Low) | 24 hours |
| Low | High | P3 (Medium) | 8 hours |
| Low | Medium | P4 (Low) | 24 hours |
| Low | Low | P4 (Low) | 72 hours |

### Impact Definitions
- **High**: Service unavailable, large number of users affected, business critical
- **Medium**: Service degraded, moderate number of users affected
- **Low**: Minor service issues, individual users affected

### Urgency Definitions  
- **High**: Business operations significantly impacted, time-sensitive
- **Medium**: Business operations somewhat impacted
- **Low**: Business operations minimally impacted

## Major Incident Management

### Major Incident Criteria
- **Service Impact**: Critical business service completely unavailable
- **User Impact**: Large number of users unable to work
- **Customer Impact**: External customers significantly affected
- **Financial Impact**: Potential for significant revenue loss
- **Regulatory Impact**: Compliance or security implications

### Major Incident Process

1. **Declaration**
   - Incident Manager or Service Desk declares major incident
   - Major Incident Manager notified immediately
   - Executive notification within 15 minutes

2. **Response Team Assembly**
   - Major Incident Manager establishes bridge call
   - Technical subject matter experts engaged
   - Business representatives included
   - External suppliers contacted if needed

3. **Communication Management**
   - Regular status updates to stakeholders
   - Executive briefings as required
   - Customer communication if applicable
   - Internal staff notifications

4. **Resolution Coordination**
   - Technical teams work in parallel where possible
   - Temporary workarounds implemented
   - Business continuity measures activated
   - Progress tracking and reporting

5. **Post-Incident Review**
   - Timeline analysis
   - Root cause analysis initiation
   - Process improvements identified
   - Lessons learned documented

## Incident Lifecycle States

1. **New**: Incident reported but not yet triaged
2. **In Progress**: Investigation and resolution in progress
3. **On Hold**: Waiting for external input or resources
4. **Resolved**: Solution implemented, awaiting user confirmation
5. **Closed**: User confirms resolution, incident closed

## Key Activities

### 1. Incident Detection and Recording
- **Detection Sources**:
  - User reports via phone, email, self-service portal
  - Monitoring system alerts
  - Automated system notifications
  - Third-party supplier notifications

- **Recording Requirements**:
  - Unique incident number
  - Date and time of occurrence
  - User contact details
  - Service affected
  - Incident description
  - Initial categorization
  - Priority assignment

### 2. Incident Categorization and Prioritization
- **Categorization**: Classify by type and affected service
- **Prioritization**: Assess business impact and urgency
- **Assignment**: Route to appropriate support group

### 3. Investigation and Diagnosis
- **Information Gathering**: Collect relevant details
- **System Analysis**: Check logs, configurations, monitoring
- **Knowledge Base Search**: Look for known solutions
- **Escalation**: Engage specialists when needed

### 4. Resolution and Recovery
- **Solution Implementation**: Apply fix or workaround
- **Testing**: Verify solution effectiveness
- **User Communication**: Inform user of resolution
- **Service Restoration**: Confirm normal operation

### 5. Incident Closure
- **User Confirmation**: Verify user satisfaction
- **Documentation**: Update incident record
- **Categorization Review**: Confirm final category
- **Closure**: Close incident in system

## ServiceNow Implementation

### Incident Form Fields
```
- Number: Automatically generated (INC0000001)
- Caller: Person reporting the incident
- Category/Subcategory: Classification for routing
- Configuration Item: Affected system/service
- Priority: Calculated from Impact × Urgency
- Assignment Group: Team responsible for resolution
- Assigned To: Individual working the incident
- State: Current lifecycle state
- Description: Detailed problem description
- Work Notes: Internal updates and actions
- Resolution Notes: Final solution details
```

### Automation Rules
- **Auto-assignment**: Route based on category
- **Escalation**: Automatic escalation if SLA breached
- **Notifications**: Email alerts for state changes
- **Integration**: Links to monitoring systems

### SLA Management
- **Response SLA**: Time to acknowledge incident
- **Resolution SLA**: Time to resolve incident
- **Escalation**: Automatic escalation if SLA at risk

## Key Performance Indicators (KPIs)

### Volume Metrics
- **Total Incidents**: Number of incidents per period
- **Incident Rate**: Incidents per user/service/time
- **Incident Trend**: Week-over-week, month-over-month changes

### Quality Metrics
- **First Call Resolution Rate**: % resolved on first contact
- **Resolution Rate**: % of incidents resolved
- **Customer Satisfaction**: User feedback scores
- **Reopen Rate**: % of incidents that reopen

### Efficiency Metrics
- **Mean Time to Resolve (MTTR)**: Average resolution time
- **Mean Time to Acknowledge**: Average response time
- **SLA Compliance**: % of incidents meeting SLA targets
- **Escalation Rate**: % of incidents escalated

### Cost Metrics
- **Cost per Incident**: Total cost divided by incident volume
- **Resource Utilization**: Staff time spent on incidents
- **Overtime Costs**: Additional costs for incident resolution

## Integration with Other Practices

### Problem Management
- Identify recurring incidents for problem investigation
- Create problems from major incidents
- Implement permanent fixes from problem resolution

### Change Enablement
- Create emergency changes for incident resolution
- Link incidents to recent changes for root cause analysis

### Service Level Management
- Report on SLA compliance
- Identify SLA breaches and trends

### Knowledge Management
- Create knowledge articles from incident resolutions
- Use knowledge base for faster resolution

### Availability Management  
- Report on service availability impacts
- Contribute to availability improvement plans

## Templates and Checklists

### Major Incident Communication Template
```
Subject: MAJOR INCIDENT - [Service Name] - [Brief Description]

Impact: [Description of business impact]
Services Affected: [List of affected services]
Users Affected: [Estimated number or groups]
Start Time: [When incident began]
Status: [Current status - Investigating/In Progress/Resolved]
Next Update: [When next update will be provided]

Contact: [Major Incident Manager contact details]
Bridge Details: [Conference call information if applicable]
```

### Incident Closure Checklist
- [ ] Solution implemented and tested
- [ ] User confirmed resolution
- [ ] All work notes documented
- [ ] Final category and priority confirmed
- [ ] Knowledge article created if applicable
- [ ] Problem record created if needed
- [ ] Customer satisfaction survey sent
- [ ] Incident closed in system

## Best Practices

### 1. Speed of Response
- Acknowledge incidents quickly (within SLA)
- Provide regular status updates
- Focus on restoration over root cause analysis

### 2. Communication
- Keep users informed throughout resolution
- Use clear, non-technical language
- Set realistic expectations

### 3. Documentation
- Record all actions and findings
- Include enough detail for knowledge transfer
- Update records in real-time

### 4. Escalation
- Escalate early when needed
- Follow defined escalation paths
- Include business impact in escalations

### 5. Learning
- Capture lessons learned
- Update procedures based on experience
- Share knowledge across teams

## Common Challenges and Solutions

### Challenge: Incident Volume Overload
**Solutions:**
- Implement self-service capabilities
- Improve automation and monitoring
- Focus on problem management to reduce repeats

### Challenge: Long Resolution Times
**Solutions:**
- Review skill levels and training needs
- Improve knowledge management
- Streamline escalation procedures

### Challenge: Poor User Communication
**Solutions:**
- Implement automated status updates
- Train staff on communication skills
- Use user-friendly status descriptions

### Challenge: SLA Breaches
**Solutions:**
- Review priority matrix and SLA targets
- Improve resource allocation
- Implement predictive escalation

---

*For ServiceNow-specific implementation details, see [ServiceNow Implementation Guide](../../implementation/servicenow-incident-management.md)*