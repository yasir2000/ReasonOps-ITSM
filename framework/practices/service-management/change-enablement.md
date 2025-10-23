# Change Enablement Practice

## Purpose

To maximize the number of successful organizational changes by ensuring that risks have been properly assessed, authorizing changes to proceed, and managing the change schedule.

## Description

**Change Enablement** (previously called Change Management) ensures that all changes are assessed, authorized, prioritized, planned, tested, implemented, documented, and reviewed in a controlled manner.

The practice encompasses:
- **Change Authority**: Decision-making for change authorization
- **Change Schedule**: Coordinated planning of all changes
- **Change Assessment**: Risk and impact evaluation
- **Change Types**: Different approaches for different change categories

## Key Concepts

### What is a Change?
The addition, modification, or removal of anything that could have a direct or indirect effect on services.

### Change Types

#### 1. Standard Changes
- **Pre-approved**: Low risk, well-understood procedure
- **No CAB Review**: Follow established procedure
- **Examples**: Password resets, standard software installations, routine maintenance

#### 2. Normal Changes  
- **CAB Assessment**: Require Change Advisory Board review
- **Risk Assessment**: Formal impact and risk analysis
- **Examples**: Major system upgrades, new service deployments, infrastructure changes

#### 3. Emergency Changes
- **Fast Track**: Urgent changes to resolve critical issues
- **Post-Implementation Review**: Reviewed after implementation
- **Examples**: Security patches, critical bug fixes, service restoration changes

## Change Enablement Model

```
Change           Change          Change         Change         Change
Request     →    Assessment  →   Authorization → Planning  →   Implementation
    ↓               ↓               ↓              ↓               ↓
Originator      Impact/Risk     Change          Detailed        Controlled
Submits         Analysis        Authority       Schedule        Deployment
Request         Evaluation      Decision        Coordination    Monitoring
```

```
Change           Change          Change         Post-Implementation
Testing     →    Deployment  →   Review    →    Closure
    ↓               ↓               ↓              ↓
Validate        Execute         Evaluate        Document
Solution        Change          Success         Lessons
Verify          Monitor         Capture         Close
Impact          Progress        Learning        Records
```

## Change Authority

### Change Authority Structure

#### Emergency Change Advisory Board (ECAB)
- **Purpose**: Rapid decision-making for emergency changes
- **Members**: Subset of CAB available 24/7
- **Decisions**: Emergency changes only
- **Timeline**: Minutes to hours

#### Change Advisory Board (CAB)
- **Purpose**: Assess and authorize normal changes
- **Members**: Cross-functional representation
- **Decisions**: Normal changes requiring assessment
- **Timeline**: Days to weeks

#### Change Manager
- **Purpose**: Day-to-day change administration
- **Authority**: Standard changes, change process management
- **Decisions**: Administrative and procedural
- **Timeline**: Immediate to days

### CAB Membership
**Core Members (Always Present):**
- Change Manager (Chair)
- Technical Representatives (Infrastructure, Applications, Security)
- Business Representatives
- Customer Representatives
- Supplier Representatives (if applicable)

**Extended Members (As Needed):**
- Subject Matter Experts
- Project Managers
- Risk and Compliance Representatives
- Finance Representatives

## Change Assessment

### Impact Assessment
Evaluation of potential effects on:
- **Services**: Availability, performance, functionality
- **Users**: Number affected, business processes impacted
- **Technology**: Systems, applications, infrastructure
- **Organization**: People, processes, costs

### Risk Assessment
Analysis of potential negative outcomes:
- **Technical Risks**: Implementation failure, rollback needs
- **Business Risks**: Service disruption, data loss
- **Security Risks**: Vulnerabilities, access control
- **Compliance Risks**: Regulatory, policy violations

### Assessment Criteria
```
Risk Level = Probability × Impact

Probability Levels:
- High (3): Very likely to occur (>70%)
- Medium (2): May occur (30-70%)  
- Low (1): Unlikely to occur (<30%)

Impact Levels:
- High (3): Significant business impact
- Medium (2): Moderate business impact
- Low (1): Minor business impact

Risk Score = Probability × Impact
- High Risk: 6-9 points
- Medium Risk: 3-4 points
- Low Risk: 1-2 points
```

## Change Lifecycle

### 1. Request for Change (RFC)
**Initiation Sources:**
- Incident resolution requirements
- Problem management solutions
- Service improvement initiatives
- Business requirements
- Regulatory compliance needs

**RFC Information Requirements:**
- Change description and rationale
- Business justification
- Impact and risk assessment
- Implementation plan
- Rollback plan
- Testing approach
- Resource requirements

### 2. Change Assessment and Authorization
**Assessment Activities:**
- Technical impact analysis
- Business impact evaluation
- Risk assessment
- Resource requirement validation
- Scheduling coordination
- Stakeholder consultation

**Authorization Outcomes:**
- **Approved**: Change authorized to proceed
- **Approved with Conditions**: Additional requirements must be met
- **Rejected**: Change not authorized
- **Deferred**: Delayed to future date

### 3. Change Planning and Scheduling
**Planning Elements:**
- Detailed implementation steps
- Resource allocation and scheduling
- Communication plan
- Testing and validation approach
- Rollback procedures
- Success criteria definition

**Schedule Coordination:**
- Change calendar maintenance
- Conflict identification and resolution
- Blackout period enforcement
- Dependency management
- Capacity planning

### 4. Change Implementation
**Implementation Controls:**
- Authorized personnel only
- Follow approved plan
- Monitor progress and impact
- Document actions taken
- Escalate issues immediately

**Implementation Verification:**
- Functional testing
- Performance validation
- Security verification
- User acceptance testing
- Business process validation

### 5. Post-Implementation Review (PIR)
**Review Objectives:**
- Assess change success
- Identify lessons learned
- Validate benefits realization
- Review process effectiveness
- Capture improvement opportunities

**Review Activities:**
- Compare actual vs. planned outcomes
- Stakeholder feedback collection
- Impact assessment validation
- Process compliance review
- Documentation update

## ServiceNow Implementation

### Change Request Form
```
Basic Information:
- Number: Automatically generated (CHG0000001)
- Type: Standard/Normal/Emergency
- Category/Subcategory: Classification
- State: Current lifecycle state
- Priority: Business priority
- Risk: Assessed risk level
- Impact: Business impact level

Planning:
- Requested By: Change originator
- Implementation Group: Team performing change
- Assigned To: Individual change coordinator
- Planned Start Date: Scheduled start time
- Planned End Date: Scheduled completion time
- Work Start: Actual start time
- Work End: Actual completion time

Description:
- Short Description: Brief change summary
- Description: Detailed change description
- Business Justification: Reason for change
- Implementation Plan: Step-by-step procedure
- Backout Plan: Rollback procedure
- Test Plan: Validation approach

Assessment:
- Configuration Items: Affected systems
- Risk Assessment: Risk analysis
- Impact Assessment: Impact analysis
- Approval: CAB decision and comments
```

### Change Workflow
1. **Draft**: Change being created/edited
2. **Assess**: Under CAB review
3. **Authorize**: Approved for implementation
4. **Scheduled**: Waiting for scheduled time
5. **Implement**: Implementation in progress
6. **Review**: Post-implementation review
7. **Closed**: Change complete and reviewed

### Change Advisory Board (CAB) Workspace
- **Pending Approvals**: Changes requiring CAB decision
- **Assessment Details**: Risk and impact analysis
- **Voting Interface**: CAB member voting mechanism  
- **Meeting Minutes**: CAB meeting documentation
- **Decision History**: Previous CAB decisions

## Change Calendar and Scheduling

### Change Calendar Purpose
- Visualize all scheduled changes
- Identify scheduling conflicts
- Manage change capacity
- Coordinate related changes
- Enforce blackout periods

### Blackout Periods
Pre-defined periods when changes are restricted:
- **Business Critical Periods**: Month-end, quarter-end
- **Peak Usage Times**: Black Friday, holiday seasons
- **Maintenance Windows**: Planned outages
- **Freeze Periods**: Code freezes, regulatory deadlines

### Scheduling Principles
1. **Minimize Business Impact**: Schedule during low-usage periods
2. **Coordinate Dependencies**: Sequence related changes appropriately
3. **Resource Availability**: Ensure skilled resources available
4. **Rollback Time**: Allow sufficient time for rollback if needed
5. **Communication Lead Time**: Provide adequate notification

## Change Types Deep Dive

### Standard Changes
**Characteristics:**
- Low risk and well-understood
- Follow documented procedure
- Pre-approved by CAB
- Minimal business impact
- Routine and repetitive

**Examples:**
- User account creation/modification
- Standard software installation
- Password resets
- Certificate renewals
- Routine maintenance tasks

**Management Approach:**
- Create change models with pre-approval
- Use service catalog for user requests
- Track volume and success rates
- Periodically review and update procedures

### Normal Changes
**Characteristics:**
- Require CAB assessment
- Moderate to high impact/risk
- Custom implementation approach
- Formal approval process
- Detailed planning required

**Examples:**
- Major application upgrades
- Infrastructure changes
- New service implementations
- Architecture modifications
- Integration projects

**Management Approach:**
- Formal RFC submission process
- Thorough impact and risk assessment
- CAB review and authorization
- Detailed implementation planning
- Post-implementation review

### Emergency Changes
**Characteristics:**
- Urgent need for implementation
- Address critical business issues
- Streamlined approval process
- Higher risk tolerance
- Post-implementation review

**Examples:**
- Critical security patches
- Production system fixes
- Service restoration changes
- Data corruption recovery
- Emergency capacity additions

**Management Approach:**
- Fast-track approval process
- Emergency CAB (ECAB) authorization
- Implement first, review later
- Expedited testing and validation
- Mandatory post-implementation review

## Key Performance Indicators (KPIs)

### Change Success Metrics
- **Change Success Rate**: % of changes completed successfully
- **Change Failure Rate**: % of changes that failed or were backed out
- **Unauthorized Changes**: Number of changes implemented without approval
- **Emergency Change Rate**: % of changes classified as emergency

### Change Efficiency Metrics
- **Change Lead Time**: Time from request to implementation
- **Change Authorization Time**: Time for CAB approval
- **Change Implementation Time**: Time to implement approved changes
- **Mean Time to Rollback**: Average time to rollback failed changes

### Change Quality Metrics
- **PIR Completion Rate**: % of changes with completed post-implementation reviews
- **Repeat Changes**: Number of follow-up changes required
- **Change-Related Incidents**: Incidents caused by changes
- **Stakeholder Satisfaction**: Satisfaction with change process

### Change Volume Metrics
- **Total Changes**: Number of changes per period
- **Change Rate**: Changes per service/system/time period
- **Change Type Distribution**: Percentage by change type
- **Change Calendar Utilization**: Percentage of available change windows used

## Integration with Other Practices

### Release Management
- **Coordination**: Changes coordinated with releases
- **Packaging**: Multiple changes bundled in releases
- **Deployment**: Release deployment requires change authorization

### [Incident Management](./incident-management.md)
- **Emergency Changes**: Incidents may require urgent changes
- **Problem Resolution**: Problem fixes implemented through changes
- **Service Restoration**: Changes to restore failed services

### [Problem Management](./problem-management.md)
- **Permanent Fixes**: Problem solutions implemented via changes
- **Workaround Implementation**: Workarounds may require changes
- **Prevention**: Changes to prevent known errors

### Service Asset and Configuration Management
- **CI Updates**: Changes update configuration item information
- **Impact Analysis**: CI relationships inform change impact assessment
- **Change Verification**: Confirm CI updates match implemented changes

### Risk Management
- **Risk Assessment**: Changes assessed for organizational risks
- **Risk Mitigation**: Changes implement risk reduction measures
- **Risk Monitoring**: Change outcomes monitored for risk realization

## Templates and Tools

### Change Request Template
```
CHANGE REQUEST FORM

Change Details:
Title: [Brief descriptive title]
Description: [Detailed description of what will change]
Business Justification: [Why this change is needed]
Category: [Hardware/Software/Process/Documentation]

Impact Assessment:
Services Affected: [List of impacted services]
Users Affected: [Number and type of users impacted]
Systems Affected: [Technical systems involved]
Business Impact: [High/Medium/Low with justification]

Risk Assessment:
Technical Risks: [Potential technical issues]
Business Risks: [Potential business impacts]  
Security Risks: [Security implications]
Risk Level: [High/Medium/Low with justification]

Implementation Plan:
Steps: [Detailed implementation steps]
Duration: [Estimated time required]
Resources: [People and tools needed]
Dependencies: [Other changes or activities required]

Testing Plan:
Test Approach: [How change will be validated]
Success Criteria: [How success will be measured]
Rollback Plan: [Steps to undo change if needed]

Schedule:
Preferred Date/Time: [When change should occur]
Alternative Dates: [Alternative scheduling options]
Blackout Periods: [Times when change cannot occur]
```

### CAB Meeting Agenda Template
```
CHANGE ADVISORY BOARD MEETING
Date: [Meeting date]
Time: [Meeting time]
Chair: [Meeting chairperson]

AGENDA:
1. Meeting Opening
   - Attendance
   - Previous meeting minutes approval
   
2. Change Pipeline Review
   - Changes scheduled for next period
   - Resource capacity review
   - Scheduling conflicts
   
3. Change Assessments
   [For each change requiring approval:]
   - RFC Number: [Change reference]
   - Presenter: [Change owner]
   - Summary: [Brief description]
   - Assessment: [Risk and impact review]
   - Recommendation: [Approve/Reject/Defer]
   - Decision: [CAB decision]
   - Actions: [Required follow-up actions]
   
4. Emergency Changes Review
   - Emergency changes since last meeting
   - Post-implementation review results
   - Lessons learned
   
5. Change Performance Review
   - Success/failure rates
   - Trending analysis
   - Process improvements
   
6. Next Meeting
   - Date and time
   - Expected agenda items

DECISIONS MADE:
[Record all CAB decisions]

ACTION ITEMS:
[Record action items with owners and due dates]
```

## Best Practices

### 1. Change Culture
- Promote "no unauthorized changes" culture
- Make change process easy to follow
- Provide training and support
- Recognize good change practices

### 2. Risk-Based Approach
- Focus assessment effort on higher-risk changes
- Use appropriate change type for each situation
- Balance speed with risk management
- Learn from change failures

### 3. Automation and Tools
- Automate standard changes where possible
- Use workflow tools for approvals
- Integrate with CI/CD pipelines
- Provide self-service capabilities

### 4. Communication
- Clear communication of change schedules
- Stakeholder notification of impacts
- Regular status updates during implementation
- Transparent reporting of change performance

### 5. Continuous Improvement
- Regular review of change performance
- Update change models based on experience
- Refine assessment criteria
- Streamline approval processes

## Common Challenges and Solutions

### Challenge: Too Many Changes to Review
**Solutions:**
- Implement effective change categorization
- Delegate appropriate authority levels
- Automate standard changes
- Focus CAB on high-risk changes only

### Challenge: Slow Change Approval Process
**Solutions:**
- Streamline assessment criteria
- Pre-approve common change types
- Use risk-based assessment levels
- Implement parallel approval workflows

### Challenge: Unauthorized Changes
**Solutions:**
- Strong governance and enforcement
- Make authorized process easy to follow
- Provide education and training
- Monitor and detect unauthorized changes

### Challenge: Change-Related Incidents
**Solutions:**
- Improve change assessment quality
- Strengthen testing requirements
- Better rollback planning
- Learn from incidents and adjust process

---

*ServiceNow-specific implementation guide is planned for future release.*