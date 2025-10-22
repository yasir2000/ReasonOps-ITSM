# Problem Management Practice

## Purpose

To reduce the likelihood and impact of incidents by identifying actual and potential causes of incidents and managing workarounds and known errors.

## Description

**Problem Management** involves activities to identify and manage the causes of incidents and potential incidents. A **problem** is a cause, or potential cause, of one or more incidents.

The practice includes:
- **Reactive Problem Management**: Triggered by one or more incidents
- **Proactive Problem Management**: Identifies problems before incidents occur

## Key Concepts

### Problem vs. Incident
- **Incident**: "Something is broken" - focus on restoration
- **Problem**: "Why did it break?" - focus on root cause

### Known Error
- A problem that has been analyzed but not resolved
- Workaround may be available
- Tracked in Known Error Database (KEDB)

### Workaround
- Technique to restore service or reduce impact
- Temporary solution until permanent fix is available
- May become permanent if cost-effective

## Process Flow

```
Problem          Problem          Problem         Root Cause      Known Error
Identification → Investigation → Diagnosis   →   Analysis    →   Record
      ↓              ↓               ↓              ↓              ↓
  Incident       Information     Symptoms      True Cause     Workaround
  Analysis       Gathering       Analysis      Identified     Development
  Monitoring     System Logs     Testing       Investigation  Documentation
  Trend          Interviews      Replication   Analysis       Knowledge Base
```

```
Solution         Error Resolution   Problem         Review &
Development  →   Control       →   Closure    →    Closure
     ↓               ↓               ↓              ↓
Change Request   Permanent Fix    Verification   Lessons
Development      Implementation   Testing        Learned
Testing          Monitoring       Confirmation   Documentation
Deployment       Validation       Sign-off       Process Improvement
```

## Problem Categories

### Reactive Problems (60-80% of problems)
**Triggered by:**
- Single major incident
- Multiple related incidents
- Pattern of recurring incidents
- Trend analysis findings

**Examples:**
- Server crashes causing multiple outages
- Recurring application errors
- Network performance degradation
- Security vulnerability exploitation

### Proactive Problems (20-40% of problems)
**Identified through:**
- Technical monitoring and alerting
- System performance analysis  
- Capacity trend analysis
- Vendor security bulletins
- Industry best practice reviews

**Examples:**
- Disk space trending toward capacity
- Memory leaks in applications
- Certificate expiration approaching
- End-of-life technology risks

## Roles and Responsibilities

### Problem Manager
- **Primary Role**: Overall problem lifecycle management
- **Responsibilities**:
  - Oversee all problem management activities
  - Prioritize problems based on business impact
  - Coordinate problem investigation teams
  - Review and approve known error records
  - Report on problem management metrics
  - Chair Problem Review Board meetings

### Problem Analyst/Investigator
- **Primary Role**: Technical problem investigation
- **Responsibilities**:
  - Analyze incidents to identify problems
  - Investigate root causes using various techniques
  - Develop and test hypotheses
  - Create and validate workarounds
  - Document findings and recommendations
  - Support solution development and testing

### Technical Subject Matter Experts (SMEs)
- **Primary Role**: Provide specialized knowledge
- **Responsibilities**:
  - Contribute technical expertise to investigations
  - Support root cause analysis activities
  - Review and validate technical findings
  - Assist with solution development
  - Provide knowledge transfer to support teams

### Problem Review Board
- **Primary Role**: Problem governance and oversight
- **Responsibilities**:
  - Review and prioritize significant problems
  - Approve resource allocation for investigations
  - Review investigation findings and recommendations
  - Make decisions on solution investments
  - Monitor problem management effectiveness

## Problem Prioritization

### Priority Matrix

| **Frequency** | **Business Impact** | **Priority** | **Investigation Timeline** |
|---------------|-------------------|--------------|---------------------------|
| High | High | P1 (Critical) | 24-48 hours |
| High | Medium | P2 (High) | 1-2 weeks |
| High | Low | P3 (Medium) | 2-4 weeks |
| Medium | High | P2 (High) | 1-2 weeks |
| Medium | Medium | P3 (Medium) | 2-4 weeks |
| Medium | Low | P4 (Low) | 1-3 months |
| Low | High | P3 (Medium) | 2-4 weeks |
| Low | Medium | P4 (Low) | 1-3 months |
| Low | Low | P4 (Low) | As resources allow |

### Frequency Definitions
- **High**: Daily occurrences or major incidents
- **Medium**: Weekly occurrences or moderate incidents  
- **Low**: Monthly occurrences or minor incidents

### Business Impact Definitions
- **High**: Critical business processes affected, revenue impact
- **Medium**: Important business processes affected, productivity impact
- **Low**: Minor business processes affected, minimal impact

## Root Cause Analysis Techniques

### 1. 5 Whys Technique
Simple technique asking "why" five times to drill down to root cause.

**Example:**
1. Why did the application crash? - Memory was exceeded
2. Why was memory exceeded? - Memory leak in the code
3. Why was there a memory leak? - Objects not properly released
4. Why weren't objects released? - Missing cleanup code
5. Why was cleanup code missing? - Code review didn't catch it

### 2. Fishbone (Ishikawa) Diagram
Visual technique categorizing potential causes:
- **People**: Skills, training, procedures
- **Process**: Methods, policies, workflows  
- **Technology**: Hardware, software, infrastructure
- **Environment**: Physical, organizational, external factors

### 3. Timeline Analysis
Chronological analysis of events leading to the problem:
- Create detailed timeline of incidents
- Identify patterns and correlations
- Map to system changes and activities
- Identify trigger events and contributing factors

### 4. Fault Tree Analysis
Logical breakdown of how failures can occur:
- Start with top-level failure event
- Break down into potential immediate causes
- Continue breaking down until root causes identified
- Identify single points of failure

## Known Error Management

### Known Error Record Contents
```
- Error ID: Unique identifier (KE0000001)
- Problem Reference: Link to originating problem
- Error Summary: Brief description of the issue
- Symptoms: How the error manifests
- Root Cause: Underlying cause of the error
- Workaround: Temporary solution if available
- Resolution Status: Investigation/Resolved/Closed
- Date Identified: When error was first identified
- Date Resolved: When permanent fix implemented
```

### Workaround Development
1. **Identify Alternatives**: Find alternative ways to deliver service
2. **Assess Feasibility**: Evaluate technical and business feasibility
3. **Test Workaround**: Validate workaround effectiveness
4. **Document Solution**: Create clear instructions
5. **Communicate**: Share with relevant teams
6. **Monitor Impact**: Track workaround usage and effectiveness

### Knowledge Base Integration
- Create knowledge articles for known errors
- Link to incident resolution procedures
- Include troubleshooting steps
- Update based on new findings

## Problem Lifecycle States

1. **New**: Problem identified but investigation not started
2. **In Progress**: Investigation actively underway
3. **Known Error**: Root cause identified, workaround may exist
4. **Resolved**: Permanent solution implemented
5. **Closed**: Solution verified effective, problem archived

## ServiceNow Implementation

### Problem Form Fields
```
- Number: Automatically generated (PRB0000001)
- Category/Subcategory: Classification for analysis
- State: Current lifecycle state
- Priority: Business priority for resolution
- Assignment Group: Team responsible for investigation
- Assigned To: Individual problem analyst
- Problem Statement: Clear description of the issue
- Root Cause: Identified underlying cause
- Workaround: Temporary solution details
- Solution: Permanent resolution approach
- Related Incidents: Links to associated incidents
- Related Changes: Links to resolution changes
```

### Problem Investigation Workspace
- **Summary Tab**: Overview and key information
- **Related Records**: Incidents, changes, CIs
- **RCA Tab**: Root cause analysis documentation
- **Tasks**: Investigation activities and assignments
- **Communication**: Stakeholder updates and notifications

### Automated Problem Creation
- **Threshold Rules**: Create problems when incident count exceeds threshold
- **Pattern Recognition**: Identify similar incidents automatically
- **Integration**: Link with monitoring systems for proactive identification

## Key Performance Indicators (KPIs)

### Effectiveness Metrics
- **Problem Resolution Rate**: % of problems permanently fixed
- **Mean Time to Identify**: Average time to identify problems
- **Mean Time to Resolve**: Average time to resolve problems
- **Incident Reduction**: % reduction in related incidents after fix

### Efficiency Metrics  
- **Cost per Problem**: Total cost divided by problems resolved
- **Resource Utilization**: Person-hours spent on problem resolution
- **Proactive vs Reactive**: Ratio of proactive to reactive problems
- **Known Error Usage**: How often workarounds are applied

### Quality Metrics
- **Root Cause Accuracy**: % of problems with correct root cause identified
- **Solution Effectiveness**: % of solutions that prevent recurrence
- **Customer Satisfaction**: Stakeholder satisfaction with problem resolution
- **Knowledge Creation**: Number of knowledge articles created

## Integration with Other Practices

### Incident Management
- **Trigger**: Major incidents or incident patterns trigger problems
- **Support**: Problems provide solutions for future incidents
- **Knowledge**: Known errors inform incident resolution

### Change Enablement
- **Solutions**: Problem solutions often require changes
- **Analysis**: Change failures may trigger problem investigations
- **Prevention**: Changes implement permanent fixes

### Continual Improvement
- **Input**: Problems identify improvement opportunities
- **Analysis**: Problem trends indicate systemic issues
- **Action**: Problem solutions drive service improvements

### Knowledge Management
- **Creation**: Problems generate valuable knowledge
- **Sharing**: Known error database shares solutions
- **Application**: Knowledge base supports investigations

### Availability Management
- **Impact**: Problems affect service availability
- **Prevention**: Problem resolution improves availability
- **Planning**: Availability plans address known errors

## Problem Review Board

### Purpose
- Provide governance and oversight for problem management
- Prioritize problems and allocate resources
- Review investigation findings and approve solutions
- Monitor problem management performance

### Membership
- **Chair**: Problem Manager or Service Owner
- **Members**: 
  - Technical SMEs from key areas
  - Business representatives
  - Change Advisory Board representative
  - Service Desk Manager
  - Major Incident Manager

### Meeting Frequency
- **Regular Meetings**: Weekly or bi-weekly
- **Emergency Sessions**: For critical problems
- **Quarterly Reviews**: Strategic assessment and planning

### Meeting Agenda
1. Problem pipeline review
2. Investigation status updates
3. New problem prioritization
4. Resource allocation decisions
5. Solution approval requests
6. Metrics and performance review
7. Process improvement discussions

## Templates and Documentation

### Problem Investigation Template
```
PROBLEM INVESTIGATION REPORT

Problem ID: [PRB number]
Problem Statement: [Clear description]
Business Impact: [Affected services and users]
Investigation Period: [Start and end dates]

TIMELINE ANALYSIS:
[Chronological sequence of events]

SYMPTOM ANALYSIS:
[Observed symptoms and their patterns]

ROOT CAUSE ANALYSIS:
Technique Used: [5 Whys, Fishbone, etc.]
Root Cause: [Identified underlying cause]
Contributing Factors: [Additional factors]

EVIDENCE:
[Supporting evidence and data]

RECOMMENDATION:
Solution: [Recommended permanent fix]
Priority: [Justification for priority]
Resources Required: [People, time, budget]
Risk Assessment: [Risks of implementing/not implementing]

WORKAROUND:
[Temporary solution if available]
Impact: [Effectiveness and limitations]
```

### Known Error Template
```
KNOWN ERROR RECORD

Error ID: KE[number]
Problem Reference: PRB[number]
Date Identified: [Date]

ERROR DESCRIPTION:
[Clear description of the error condition]

SYMPTOMS:
- [Observable symptoms]
- [Impact on users/services]
- [Related error messages]

ROOT CAUSE:
[Underlying cause of the error]

WORKAROUND:
Steps: [Detailed workaround procedure]
Limitations: [What the workaround doesn't address]
Monitoring: [How to detect if workaround is needed]

PERMANENT SOLUTION:
Status: [In Development/Testing/Approved/Implemented]
Target Date: [Expected resolution date]
Owner: [Responsible person/team]
```

## Best Practices

### 1. Investigation Approach
- Focus on patterns rather than individual incidents
- Use data-driven analysis techniques
- Involve right technical expertise early
- Document findings throughout investigation

### 2. Root Cause Analysis
- Use appropriate RCA techniques for the situation
- Look beyond immediate causes to systemic issues
- Validate findings with evidence
- Consider multiple contributing factors

### 3. Solution Development
- Evaluate cost-benefit of permanent solutions
- Consider short-term workarounds
- Test solutions thoroughly before implementation
- Plan for solution rollback if needed

### 4. Knowledge Management
- Create searchable known error records
- Update knowledge base with findings
- Share lessons learned across teams
- Maintain current and accurate documentation

### 5. Continuous Improvement
- Regular review of problem trends
- Assess effectiveness of solutions
- Refine investigation techniques
- Update procedures based on experience

## Common Challenges and Solutions

### Challenge: Too Many Problems to Investigate
**Solutions:**
- Implement effective prioritization criteria
- Focus on high-impact, high-frequency problems
- Use automated pattern recognition
- Dedicate sufficient resources

### Challenge: Poor Root Cause Analysis
**Solutions:**
- Train staff in RCA techniques
- Use structured investigation methods
- Validate findings with evidence
- Review and learn from past investigations

### Challenge: Workaround Becomes Permanent
**Solutions:**
- Track workaround usage and effectiveness
- Set target dates for permanent solutions
- Regular review of known errors
- Management commitment to permanent fixes

### Challenge: Integration with Incident Management
**Solutions:**
- Clear escalation criteria from incidents to problems
- Regular review of incident patterns
- Automated problem creation rules
- Joint training for incident and problem teams

---

*For ServiceNow-specific implementation details, see [ServiceNow Implementation Guide](../../implementation/servicenow-problem-management.md)*