### **Automated Workflow: Wazuh Login Failure Detection to O365 User Check**

**Objective:**
This document outlines the procedure to create a security workflow using Shuffle.io. The workflow automatically triggers on a "failed login" alert from Wazuh, retrieves the corresponding user's account status from Microsoft 365/Entra ID, and sends a summary email notification to the security team.

**Prerequisites:**
*   A functional Wazuh Manager monitoring a Windows endpoint.
*   A functional Shuffle.io instance.
*   Administrative privileges in Microsoft Entra ID (Office 365) to create an App Registration.
*   **Microsoft Graph API Credentials**:
    *   **Tenant ID**
    *   **Client ID**
    *   **Client Secret**
    *   Required API Permissions (Type: **Application**): `User.Read.All`. Admin Consent must be granted for this permission in Azure.

---

### **Procedure**

#### **Part 1: Configure Wazuh to Forward Alerts**

1.  Connect to your Wazuh Manager via SSH.
2.  Edit the Wazuh configuration file: `nano /var/ossec/etc/ossec.conf`.
3.  Inside the `<ossec_config>` section, add the following `<integration>` block. You will get the `YOUR_SHUFFLE_WEBHOOK_URL` in the next part. For now, know that this is where it goes. This configuration tells Wazuh to send alerts for Windows logon failures (rule `60122`) to Shuffle.

    ```xml
    <integration>
      <name>shuffle</name>
      <hook_url>YOUR_SHUFFLE_WEBHOOK_URL</hook_url>
      <rule_id>60122</rule_id>
      <alert_format>json</alert_format>
    </integration>
    ```
4.  Save the file. You will restart the service after creating the webhook.

#### **Part 2: Create the Shuffle Workflow**

1.  In your Shuffle instance, go to **Workflows** and click **New Workflow**. Name it something like "Wazuh Login Failure Investigation".
2.  From the left menu, drag the **Webhook** trigger onto the canvas.
3.  Click the Webhook node. On the right panel, **copy the generated Webhook URL**.
4.  Go back to your Wazuh Manager's `ossec.conf` file and paste the copied URL into the `<hook_url>` field.
5.  Now, restart the Wazuh manager to apply all changes:
    ```bash
    systemctl restart wazuh-manager
    ```

#### **Part 3: Generate Test Data to Find Your Variables**

To configure the next steps correctly, you need a real alert from Wazuh so you can see the exact structure of the data.

1.  On your monitored Windows machine, intentionally cause a failed login event (e.g., type the wrong password for a known user).
2.  In the Shuffle UI, go to the **Executions** page for your workflow. A new execution should appear. Click on it.
3.  Click the `Webhook` icon in the execution graph and expand the **Execution Argument** on the right.
4.  Carefully examine the JSON data to find the exact paths for the following fields. **Write them down.** Common paths are:
    *   **Username:** Look for `targetUserName`. The path might be `$exec.data.win.eventdata.targetUserName`.
    *   **Source IP:** Look for `ipAddress`. The path might be `$exec.data.win.eventdata.ipAddress`.
    *   **Hostname:** Look for `agent.name`. The path would be `$exec.agent.name`.

#### **Part 4: Configure the Workflow Actions**

1.  **Configure Microsoft Graph User Check:**
    *   Drag the **Microsoft Graph** app onto the canvas and connect the `Webhook` node to it.
    *   **Action**: `Get User`.
    *   **Authentication**: Enter your **Tenant ID**, **Client ID**, and **Client Secret**.
    *   **Parameters**: In the `User ID` field, enter the variable path for the username you found in Part 3 (e.g., `$exec.data.win.eventdata.targetUserName`).

2.  **Configure Email Notification:**
    *   Drag the **Email** app onto the canvas and connect the `Microsoft Graph` node to it.
    *   **Parameters**:
        *   **recipients**: Enter the email address where you want to receive notifications (e.g., `soc@yourcompany.com`).
        *   **subject**: `Shuffle Report: User Login Failure for $exec.data.win.eventdata.targetUserName` (Use your variable path).
        *   **body**: Paste the following template. **Important**: You must use the exact variable paths you identified in Part 3. The paths below are common examples. The `{{$Microsoft_Graph_1...}}` paths refer to the results from the step above.

        ```
        A user login failure has been detected by Wazuh and processed by Shuffle.

        Alert Details:
        - Time: $exec.timestamp
        - Description: $exec.rule.description
        - Host: $exec.agent.name
        - User Attempted: $exec.data.win.eventdata.targetUserName
        - Source IP: $exec.data.win.eventdata.ipAddress

        Automated Investigation:
        - O365 User Status: Queried.
        - User Display Name: {{$Microsoft_Graph_1.result.displayName}}
        - User Account Enabled: {{$Microsoft_Graph_1.result.accountEnabled}}

        Please review for suspicious activity.
        ```

#### **Part 5: Final Testing**

1.  Ensure your workflow has been saved.
2.  On your monitored Windows machine, cause one more login failure.

**Expected Outcome:**
Within a minute, you should receive an email with the subject "Shuffle Report: User Login Failure...". The body of the email will contain the details of the failed login attempt and the user's account status from Microsoft 365 (e.g., Display Name, Account Enabled: true/false).