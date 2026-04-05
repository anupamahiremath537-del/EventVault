// utils/email.js - Updated to use Resend API for Render compatibility
const RESEND_API_KEY = process.env.RESEND_API_KEY;

module.exports = {
  async sendEmail(to, subject, text, html, attachments = []) {
    if (!RESEND_API_KEY) {
      console.error('[Email ERROR] RESEND_API_KEY is not configured on Render!');
      return { error: 'Email API key missing' };
    }

    try {
      // Convert attachments if any (Resend expects filename and content/path)
      const formattedAttachments = attachments.map(a => ({
        filename: a.filename,
        content: a.content.toString('base64')
      }));

      const response = await fetch('https://api.resend.com/emails', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${RESEND_API_KEY}`
        },
        body: JSON.stringify({
          from: `${process.env.EMAIL_FROM_NAME || 'EventVault'} <onboarding@resend.dev>`, 
          to: [to],
          subject: subject,
          text: text,
          html: html || text.replace(/\n/g, '<br>'),
          attachments: formattedAttachments.length > 0 ? formattedAttachments : undefined
        })
      });

      const data = await response.json();

      if (response.ok) {
        console.log(`[Email SENT via API] To: ${to}, ID: ${data.id}`);
        return { success: true, messageId: data.id };
      } else {
        console.error('[Email API ERROR]', data);
        return { error: data.message || 'API Error' };
      }
    } catch (err) {
      console.error(`[Email FATAL ERROR] To: ${to}, Details: ${err.message}`);
      return { error: err.message };
    }
  },

  async sendBroadcast(emails, subject, message, html = null, attachments = []) {
    const results = { success: 0, failure: 0 };
    const uniqueEmails = [...new Set(emails.filter(e => !!e))];
    
    console.log(`[Email Broadcast] Starting via API for ${uniqueEmails.length} recipients...`);
    
    // We can send faster with API
    for (const email of uniqueEmails) {
      const res = await this.sendEmail(email, subject, message, html, attachments);
      if (res.success) results.success++;
      else results.failure++;
      
      // Small 100ms delay to respect rate limits
      await new Promise(r => setTimeout(r, 100));
    }
    
    return results;
  }
};
