import logging
from odoo import api, models, fields, _
from odoo.exceptions import UserError, ValidationError
from odoo.addons.base.models.ir_mail_server import (
    extract_rfc2822_addresses,
    MailDeliveryException,
    _test_logger,
)
from odoo.tools import ustr, pycompat, formataddr
from email.header import decode_header
from email.utils import parseaddr, COMMASPACE, getaddresses
from postmarker.core import PostmarkClient

_logger = logging.getLogger(__name__)

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from email.message import EmailMessage
import base64


def convert_to_mime(email_msg: EmailMessage):
    # Create a MIMEMultipart object
    mime_msg = MIMEMultipart()
    text_body = ""
    html_body = ""

    for part in email_msg.iter_parts():
        payload = part.get_payload(decode=True)
        # Extract TextBody and HtmlBody
        text_body = MIMEText(payload, "plain", 'utf-8')
        html_body = MIMEText(payload, "html", 'utf-8')

    # Attach text body if available
    if text_body:
        mime_msg.attach(text_body)

    # Attach HTML body if available
    if html_body:
        mime_msg.attach(html_body)

    # Attach default if neither are available
    if not text_body and html_body:
        raise ValidationError(_("You can not send an empty message!"))

    # Handle attachments
    for part in email_msg.iter_parts():
        content_type = part.get_content_type()
        payload = part.get_payload(decode=True)
        if payload is None:
            continue
        elif payload is not None:
            mime_part = MIMEBase(part.get_content_maintype(), part.get_content_subtype())
            mime_part.set_payload(payload)
            encoders.encode_base64(mime_part)
            mime_part.add_header('Content-Disposition', f'attachment; filename="{part.get_filename()}"')
            mime_msg.attach(mime_part)

    # Copy headers from the original message
    for key, value in email_msg.items():
        mime_msg[key] = value

    return mime_msg



# def encode_rfc2822_address_header(header_text):
#     """If ``header_text`` contains non-ASCII characters,
#     attempts to locate patterns of the form
#     ``"Name" <address@domain>`` and replace the
#     ``"Name"`` portion by the RFC2047-encoded
#     version, preserving the address part untouched.
#     """
#
#     def encode_addr(addr):
#         name, email = addr
#         try:
#             return formataddr((name, email), "ascii")
#         except UnicodeEncodeError:
#             _logger.warning(
#                 _("Failed to encode the address %s\n" "from mail header:\n%s")
#                 % (addr, header_text)
#             )
#             return ""
#
#     addresses = getaddresses([pycompat.to_native(ustr(header_text))])
#     return COMMASPACE.join(a for a in (encode_addr(addr) for addr in addresses) if a)


class IrMailServer(models.Model):
    _inherit = "ir.mail_server"

    default_sender_signature = fields.Char(string="Default Sender Signature")

    def connect(
            self,
            host=None,
            port=None,
            user=None,
            password=None,
            encryption=None,
            smtp_from=None,
            ssl_certificate=None,
            ssl_private_key=None,
            smtp_debug=False,
            mail_server_id=None,
            allow_archived=False,
    ):

        if self._is_test_mode():
            return

        mail_server = smtp_encryption = None
        if mail_server_id:
            mail_server = self.sudo().browse(mail_server_id)
            if not allow_archived and not mail_server.active:
                raise UserError(
                    _(
                        'The server "%s" cannot be used because it is archived.',
                        mail_server.display_name,
                    )
                )
        elif not host:
            mail_server, smtp_from = self.sudo()._find_mail_server(smtp_from)

        if not mail_server:
            mail_server = self.env["ir.mail_server"]

        if "postmark" not in mail_server.smtp_host:
            return super(IrMailServer, self).connect(
                self,
                host=host,
                port=port,
                user=user,
                password=password,
                encryption=encryption,
                smtp_from=smtp_from,
                ssl_certificate=ssl_certificate,
                ssl_private_key=ssl_private_key,
                smtp_debug=smtp_debug,
                mail_server_id=mail_server_id,
                allow_archived=allow_archived,
            )
        return None

    @api.model
    def send_email(
            self,
            message="",
            mail_server_id=None,
            smtp_server=None,
            smtp_port=None,
            smtp_user=None,
            smtp_password=None,
            smtp_encryption=None,
            smtp_ssl_certificate=None,
            smtp_ssl_private_key=None,
            smtp_debug=False,
            smtp_session=None,
    ):
        """overloading send_email method to send email with postmark api if postmark server is used"""
        if self._is_test_mode():
            _test_logger.info("skip sending email in test mode")
            return message["Message-Id"]

        if mail_server_id:
            mail_server = self.sudo().browse(mail_server_id)
        else:
            mail_server = self.sudo().search(
                [("active", "=", True)], order="sequence", limit=1
            )

        # if server is not postmark server call super

        if "postmark" not in mail_server.smtp_host:
            return super(IrMailServer, self).send_email(
                message,
                mail_server_id=mail_server_id,
                smtp_server=smtp_server,
                smtp_port=smtp_port,
                smtp_user=smtp_user,
                smtp_password=smtp_password,
                smtp_encryption=smtp_encryption,
                smtp_ssl_certificate=smtp_ssl_certificate,
                smtp_ssl_private_key=smtp_ssl_private_key,
                smtp_debug=smtp_debug,
                smtp_session=smtp_session,
            )

        # Use the default bounce address **only if** no Return-Path was
        # provided by caller.  Caller may be using Variable Envelope Return
        # Path (VERP) to detect no-longer valid email addresses.
        smtp_from = (
                message["Return-Path"]
                or self._get_default_bounce_address()
                or message["From"]
        )
        assert (
            smtp_from
        ), "The Return-Path or From header is required for any outbound email"

        # The email's "Envelope From" (Return-Path), and all recipient addresses must only contain ASCII characters.
        from_rfc2822 = extract_rfc2822_addresses(smtp_from)
        assert from_rfc2822, (
                                 "Malformed 'Return-Path' or 'From' address: %r - "
                                 "It should contain one valid plain ASCII email"
                             ) % smtp_from
        # use last extracted email, to support rarities like 'Support@MyComp <support@mycompany.com>'
        smtp_from = from_rfc2822[-1]
        email_to = message["To"]
        email_cc = message["Cc"]
        email_bcc = message["Bcc"]
        del message["Bcc"]

        smtp_to_list = [
            address
            for base in [email_to, email_cc, email_bcc]
            for address in extract_rfc2822_addresses(base)
            if address
        ]
        assert smtp_to_list, self.NO_VALID_RECIPIENT

        x_forge_to = message["X-Forge-To"]
        if x_forge_to:
            # `To:` header forged, e.g. for posting on mail.channels, to avoid confusion
            del message["X-Forge-To"]
            del message["To"]  # avoid multiple To: headers!
            message["To"] = x_forge_to
        # Postmark doesnt permit if from address have a sender signature.

        from_name, from_email = parseaddr(
            extract_rfc2822_addresses(decode_header(message["From"]))
        )
        default_name, default_email = parseaddr(mail_server.default_sender_signature)
        signature_domain = default_email.split("@")[1]
        if signature_domain not in from_email:
            del message["From"]
            message["From"] = default_email
            # message["From"] = encode_rfc2822_address_header(
            #     mail_server.default_sender_signature
            # )

        try:
            mime_message = convert_to_mime(message)
            postmark = PostmarkClient(server_token=mail_server.smtp_pass)
            result = postmark.emails.send(message=mime_message)

        except Exception as e:
            msg = _("Mail delivery failed via Postmark API: " + str(e))
            _logger.info(msg)
            raise MailDeliveryException(_("Mail Delivery Failed"), msg)
        return result["MessageID"]
