<html>
<head>
<title>3D Pay Ödeme Sayfasi</title>
<meta http-equiv="Content-Language" content="tr">
  <meta http-equiv="Content-Type" content="text/html; charset=ISO-8859-9">
  <meta http-equiv="Pragma" content="no-cache">
  <meta http-equiv="Expires" content="now">

3D_PAY / 3D_HALF / 3D_FULL / 3D_OOS_FULL / 3D_OOS_PAY /3D_OOS_HALF ve OOS_PAY ICIN GUVENLIK DOGRULAMALI DONUS SAYFASIDIR...
</head>
<body>
   <!-- #include file = "MACSHA1.asp" -->
    <%

        strMDStatus = Request.Form("mdstatus")
	model = Request.Form("secure3dsecuritylevel")
	If Not model = "OOS_PAY" Then
	Response.Write("<br>")
	Response.write STRING(60, "-")
	Response.Write("<br>mdstatus için önemli not: bu değer sadece 3d sifre dogrulaması ilgili sonuç verir.")
	Response.Write("<br>")
	Response.write STRING(60, "-") & ("<br>")

	Response.Write("<br>3d sorgulamasının dönüş bilgisi: ")
	

        If strMDStatus = 1 Then  
	 Response.Write("<br>3D dönüs mdstatus 1 Tam Doğrulama ")
        ElseIf strMDStatus = 2 Then
            Response.Write("<br>3D dönüs mdstatus 2 Kart Sahibi veya bankası sisteme kayıtlı değil")
        ElseIf strMDStatus = 3 Then
            Response.Write("<br>3D dönüs mdstatus 3 Kartın bankası sisteme kayıtlı değil")
        ElseIf strMDStatus = 4 Then
            Response.Write("<br>3D dönüs mdstatus 4 Doğrulama denemesi, kart sahibi sisteme daha sonra kayıt olmayı seçmis")
        ElseIf strMDStatus = 5 Then
            Response.Write("<br>3D dönüs mdstatus 5 Doğrulama yapılamıyor")
	        ElseIf strMDStatus = 6 Then
            Response.Write("<br>3D dönüs mdstatus 6 3D kaydınız henüz tamamlanmamıs, ilk tanımlamada visa master kaydı 7-10 gün sürebilmektedir..")
        ElseIf strMDStatus = 7 Then
            Response.Write  ("<br> !!!!!3D Alınan hata mdstatus 7 - bu durumda önce mderrormessage bakınız !!!!!")
	    Response.Write("<br> * Kullanım tipi desteklenmiyor ise kullanılan 3d modeliniz hatalı veya 3d tanımınız bulunmuyor")
	    Response.Write("<br> * Guvenlik Kodu hatali mesajı için 8. sayfa faydalı olacaktır http://www.garantipos.com.tr/mailing/Gvpkullanim.pdf <br>")
	 
        ElseIf strMDStatus = 8 Then
            Response.Write("<br>Bilinmeyen Kart No")
        ElseIf strMDStatus = 0 Then
            Response.Write("<br>3D Doğrulama Basarısız, 3-D Secure imzası geçersiz. mdstatus 0 ")
        End If
	
	else
	Response.Write UCase ("<br>OOS_PAY 3d sorgulamasIz modeldir..")
      End If 

    %>

    <%

detail = "1"   ' dönen tüm değerleri yazdırmak için 1 olmalı hata ayıklamak için.

	Response.Write("<br><br> Provizyon doğrulama:<br>")
    	sonuc = ""
	isValidHash = False
	responseHashparams =  request.form("hashparams")
	responseHashparams = LCase (responseHashparams)
	responseHashparamsval = request.form("hashparamsval")
	responseHash = request.form("hash")
	storekey = "12345678" //TODO STORE KEY OF TERMINAL /store key değerimiz.
	

	br = "<br>"
        
	If Not IsEmpty(request.form("hashparams")) Then 
			digestData = ""
			paramList = Split(responseHashparams,":")
            paramCount = Ubound(paramList)
			
            for i = 0 to paramCount
                param = paramList(i)
                value = request.form(param)
                if(value = null) then
                   value = ""
                end if 
                digestData = digestData & value
            next			
            
		hashCalculated = b64_sha1(digestData & storekey)
	
			

			if(responseHash = hashCalculated) then 
				Response.Write(br & "***Mesaj Bankadan Geliyor***")
				sonuc = request.form("procreturncode")
				isValidHash = True
			else
				Response.Write(br & "!!!!!Dikkat Mesaj Bankadan Gelmiyor!!!!!")
				Response.Write(br & "!!!!!veya store keyiniz hatalı !!!!!")
				Response.Write(br & "RESPONSE HASH : [" & responseHash & "]")
				Response.Write(br & "CALCULATED HASH : ["& hashCalculated &"]")
			end if 
	  		else
			Response.Write(br & "!!!!!FATAL ERROR/INTEGRATION ERROR!!!!!")
			Response.Write(br & "response :" &request.form("response"))
			Response.Write(br & "procreturncode :" & request.form("procreturncode"))
			Response.Write(br & "mderrormessage :" & request.form("mderrormessage"))
	  		end if 
	  
	  Response.Write(br & " Validation :" & isValidHash)
		
	Response.Write(br)

	if isValidHash = True then

	        'isValidHash True  ve  procreturncode 00 döndüğünde işlem başarılıdır.
           	If sonuc = "00" Then
                Response.Write "İşlem Onaylandı"
		Response.Write(br & "Onay no :" & request.form("authcode"))
           	Else
		Response.Write "Red onaylanmadı <br />"
               	Response.Write "İşlem Başarısız.. "
		Response.Write(br & "Hata kodu :" & request.form("procreturncode") & br & br)
	      
               Response.Write strErrorMsg ' Veya strSysErrMsg Veya kendi mesajımızı da yazabiliriz.
			 '  Response.Redirect "http://localhost/asp/asptest/HATA.asp"
           	End If
	
	End If	 
	
	if detail = 1 Then 
	%>
	<td><b><br> Yapıyı anlamak için dönen tüm değerlerin listesi : </b></td><br>
        <table border="1">
        <tr>
            <td><b>Parametre Ismi</b></td>
            <td><b>Parametre Degeri</b></td>
        </tr>
	<%

	        For each obj in request.form
           	response.write("<tr><td>" & obj &"</td><td>" & request.form(obj) & "</td></tr>")
        Next
	End If	


    %>


</body>
</html>