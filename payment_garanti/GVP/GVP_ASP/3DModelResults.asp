<html>
<head>
    <title></title>
    <script language="javascript" type="text/javascript" runat="server">
        
        var hexcase = 1;
        var b64pad = "=";
        var chrsz = 8;

        function hex_sha1(s) { return binb2hex(core_sha1(str2binb(s), s.length * chrsz)); }
        function b64_sha1(s) { return binb2b64(core_sha1(str2binb(s), s.length * chrsz)); }
        function str_sha1(s) { return binb2str(core_sha1(str2binb(s), s.length * chrsz)); }
        function hex_hmac_sha1(key, data) { return binb2hex(core_hmac_sha1(key, data)); }
        function b64_hmac_sha1(key, data) { return binb2b64(core_hmac_sha1(key, data)); }
        function str_hmac_sha1(key, data) { return binb2str(core_hmac_sha1(key, data)); }

        function sha1_vm_test() {
            return hex_sha1("abc") == "a9993e364706816aba3e25717850c26c9cd0d89d";
        }

        function core_sha1(x, len) {

            x[len >> 5] |= 0x80 << (24 - len % 32);
            x[((len + 64 >> 9) << 4) + 15] = len;

            var w = Array(80);
            var a = 1732584193;
            var b = -271733879;
            var c = -1732584194;
            var d = 271733878;
            var e = -1009589776;

            for (var i = 0; i < x.length; i += 16) {
                var olda = a;
                var oldb = b;
                var oldc = c;
                var oldd = d;
                var olde = e;

                for (var j = 0; j < 80; j++) {
                    if (j < 16) w[j] = x[i + j];
                    else w[j] = rol(w[j - 3] ^ w[j - 8] ^ w[j - 14] ^ w[j - 16], 1);
                    var t = safe_add(safe_add(rol(a, 5), sha1_ft(j, b, c, d)),
                           safe_add(safe_add(e, w[j]), sha1_kt(j)));
                    e = d;
                    d = c;
                    c = rol(b, 30);
                    b = a;
                    a = t;
                }

                a = safe_add(a, olda);
                b = safe_add(b, oldb);
                c = safe_add(c, oldc);
                d = safe_add(d, oldd);
                e = safe_add(e, olde);
            }
            return Array(a, b, c, d, e);

        }

        function sha1_ft(t, b, c, d) {
            if (t < 20) return (b & c) | ((~b) & d);
            if (t < 40) return b ^ c ^ d;
            if (t < 60) return (b & c) | (b & d) | (c & d);
            return b ^ c ^ d;
        }

        function sha1_kt(t) {
            return (t < 20) ? 1518500249 : (t < 40) ? 1859775393 :
             (t < 60) ? -1894007588 : -899497514;
        }

        function core_hmac_sha1(key, data) {
            var bkey = str2binb(key);
            if (bkey.length > 16) bkey = core_sha1(bkey, key.length * chrsz);

            var ipad = Array(16), opad = Array(16);
            for (var i = 0; i < 16; i++) {
                ipad[i] = bkey[i] ^ 0x36363636;
                opad[i] = bkey[i] ^ 0x5C5C5C5C;
            }

            var hash = core_sha1(ipad.concat(str2binb(data)), 512 + data.length * chrsz);
            return core_sha1(opad.concat(hash), 512 + 160);
        }

        function safe_add(x, y) {
            var lsw = (x & 0xFFFF) + (y & 0xFFFF);
            var msw = (x >> 16) + (y >> 16) + (lsw >> 16);
            return (msw << 16) | (lsw & 0xFFFF);
        }

        function rol(num, cnt) {
            return (num << cnt) | (num >>> (32 - cnt));
        }

        function str2binb(str) {
            var bin = Array();
            var mask = (1 << chrsz) - 1;
            for (var i = 0; i < str.length * chrsz; i += chrsz)
                bin[i >> 5] |= (str.charCodeAt(i / chrsz) & mask) << (32 - chrsz - i % 32);
            return bin;
        }

        function binb2str(bin) {
            var str = "";
            var mask = (1 << chrsz) - 1;
            for (var i = 0; i < bin.length * 32; i += chrsz)
                str += String.fromCharCode((bin[i >> 5] >>> (32 - chrsz - i % 32)) & mask);
            return str;
        }

        function binb2hex(binarray) {
            var hex_tab = hexcase ? "0123456789ABCDEF" : "0123456789abcdef";
            var str = "";
            for (var i = 0; i < binarray.length * 4; i++) {
                str += hex_tab.charAt((binarray[i >> 2] >> ((3 - i % 4) * 8 + 4)) & 0xF) +
               hex_tab.charAt((binarray[i >> 2] >> ((3 - i % 4) * 8)) & 0xF);
            }
            return str;
        }

        function binb2b64(binarray) {
            var tab = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwx  yz0123456789+/";
            var str = "";
            for (var i = 0; i < binarray.length * 4; i += 3) {
                var triplet = (((binarray[i >> 2] >> 8 * (3 - i % 4)) & 0xFF) << 16)
                    | (((binarray[i + 1 >> 2] >> 8 * (3 - (i + 1) % 4)) & 0xFF) << 8)
                    | ((binarray[i + 2 >> 2] >> 8 * (3 - (i + 2) % 4)) & 0xFF);
                for (var j = 0; j < 4; j++) {
                    if (i * 8 + j * 6 > binarray.length * 32) str += b64pad;
                    else str += tab.charAt((triplet >> 6 * (3 - j)) & 0x3F);
                }
            }
            return str;
        }
    </script>
</head>
<body>
    <%
        strMDStatus = Request.Form("mdstatus")

        If strMDStatus = 1 Then
            Response.Write("Tam Doðrulama")
        ElseIf strMDStatus = 2 Then
            Response.Write("Kart Sahibi veya bankasý sisteme kayýtlý deðil")
        ElseIf strMDStatus = 3 Then
            Response.Write("Kartýn bankasý sisteme kayýtlý deðil")
        ElseIf strMDStatus = 4 Then
            Response.Write("Doðrulama denemesi, kart sahibi sisteme daha sonra kayýt olmayý seçmiþ")
        ElseIf strMDStatus = 5 Then
            Response.Write("Doðrulama yapýlamýyor")
        ElseIf strMDStatus = 7 Then
            Response.Write("Sistem Hatasý")
        ElseIf strMDStatus = 8 Then
            Response.Write("Bilinmeyen Kart No")
        ElseIf strMDStatus = 0 Then
            Response.Write("Doðrulama Baþarýsýz, 3-D Secure imzasý geçersiz.")
        End If
        
        'Tam Doðrulama, Kart Sahibi veya bankasý sisteme kayýtlý deðil, Kartýn bankasý sisteme kayýtlý deðil
        'Doðrulama denemesi, kart sahibi sisteme daha sonra kayýt olmayý seçmiþ responselarýný alan
        'iþlemler için Provizyon almaya çalýþýyoruz
        If strMDStatus = 1 Or strMDStatus = 2 Or strMDStatus = 3 Or strMDStatus = 4 Then

            strMode = Request.Form("mode")
            strVersion = Request.Form("apiversion")
            strTerminalID = Request.Form("clientid")
            strTerminalID_ = "0" & Request.Form("clientid")
            strProvisionPassword = "XXXXXX" 'Terminal UserID þifresi
            strProvUserID = Request.Form("terminalprovuserid")
            strUserID = Request.Form("terminaluserid")
            strMerchantID = Request.Form("terminalmerchantid")
            strIPAddress = Request.Form("customeripaddress")
            strEmailAddress = Request.Form("customeremailaddress")
            strOrderID = Request.Form("orderid")
            strNumber = "" 'Kart bilgilerinin boþ gitmesi gerekiyor
            strExpireDate = "" 'Kart bilgilerinin boþ gitmesi gerekiyor
            strCVV2 = "" 'Kart bilgilerinin boþ gitmesi gerekiyor
            strAmount = Request.Form("txnamount")
            strCurrencyCode = Request.Form("txncurrencycode")
            strInstallmentCount = Request.Form("txninstallmentcount")
            strCardholderPresentCode = "13" '3D Model iþlemde bu deðer 13 olmalý
            strType = Request.Form("txntype")
            strMotoInd = "N"
            strAuthenticationCode = Server.URLEncode(Request.Form("cavv"))
            strSecurityLevel = Server.URLEncode(Request.Form("eci"))
            strTxnID = Server.URLEncode(Request.Form("xid"))
            strMD = Server.URLEncode(Request.Form("md"))
            SecurityData = hex_sha1(strProvisionPassword + strTerminalID_)
            HashData = hex_sha1(strOrderID + strTerminalID + strAmount + SecurityData) 'Daha kýsýtlý bilgileri HASH ediyoruz.
            strHostAddress = "https://sanalposprov.garanti.com.tr/VPServlet" 'Provizyon için xml'in post edileceði adres

            'Provizyona Post edilecek XML Þablonu
            strXML = "<?xml version=""1.0"" encoding=""UTF-8""?>" & _
                     "<GVPSRequest>" & _
                     "<Mode>" & strMode & "</Mode>" & _
                     "<Version>" & strVersion & "</Version>" & _
                     "<ChannelCode></ChannelCode>" & _
                     "<Terminal><ProvUserID>" & strProvUserID & "</ProvUserID><HashData>" & HashData & "</HashData><UserID>" & strUserID & "</UserID><ID>" & strTerminalID & "</ID><MerchantID>" & strMerchantID & "</MerchantID></Terminal>" & _
                     "<Customer><IPAddress>" & strIPAddress & "</IPAddress><EmailAddress>" & strEmailAddress & "</EmailAddress></Customer>" & _
                     "<Card><Number></Number><ExpireDate></ExpireDate><CVV2></CVV2></Card>" & _
                     "<Order><OrderID>" & strOrderID & "</OrderID><GroupID></GroupID><AddressList><Address><Type>S</Type><Name></Name><LastName></LastName><Company></Company><Text></Text><District></District><City></City><PostalCode></PostalCode><Country></Country><PhoneNumber></PhoneNumber></Address></AddressList></Order>" & _
                     "<Transaction>" & _
                     "<Type>" & strType & "</Type><InstallmentCnt>" & strInstallmentCount & "</InstallmentCnt><Amount>" & strAmount & "</Amount><CurrencyCode>" & strCurrencyCode & "</CurrencyCode><CardholderPresentCode>" & strCardholderPresentCode & "</CardholderPresentCode><MotoInd>" & strMotoInd & "</MotoInd>" & _
                     "<Secure3D><AuthenticationCode>" & strAuthenticationCode & "</AuthenticationCode><SecurityLevel>" & strSecurityLevel & "</SecurityLevel><TxnID>" & strTxnID & "</TxnID><Md>" & strMD & "</Md></Secure3D>" & _
                     "</Transaction>" & _
                     "</GVPSRequest>"
                     
            Set SrvHTTPS = Server.CreateObject("MSXML2.ServerXMLHTTP")
            Set XMLSend = Server.CreateObject("MSXML2.DOMDocument")
           
            XMLSend.async = false
            XMLSend.resolveExternals = false

            SrvHTTPS.open "POST", strHostAddress, false
            SrvHTTPS.setRequestHeader "Content-Type","application/x-www-form-urlencoded"
            SrvHTTPS.send "data="+strXML

            Set xmlDoc2 = CreateObject("MSXML2.DOMDocument")
            xmlDoc2.setProperty "ServerHTTPRequest", True
            xmlDoc2.async = True
            xmlDoc2.LoadXML SrvHTTPS.responseText

            Response.Write "<br><b>Giden Ýstek</b><br>"
            Response.Write strXML
            Response.Write "<br>"
            Response.Write "<br><b>Gelen Yanýt</b><br>"
            Response_Doc = SrvHTTPS.responseText
            Response_Doc = Replace (Response_Doc,"<","&lt;")
            Response_Doc = Replace (Response_Doc,">","&gt;")
            Response.Write Response_Doc & "<br>"

        End If
        
        For each obj in request.form
            Response.Write("<br>" & obj & " :" & request.form(obj) & vbcrlf)
        Next
    %>

</body>
</html>