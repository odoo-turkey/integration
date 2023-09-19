<html>
<head>
    <title></title>
</head>
<body>

    <!-- #include file = "MACSHA1.asp" -->
    <%
    isValidHash = False
	responseHashparams = request.form("hashparams")
	responseHashparamsval = request.form("hashparamsval")
	responseHash = request.form("hash")
	storekey = "XXXXXXXX" //TODO STORE KEY OF TERMINAL 
	br = "<br>"

	Response.Write(br & "RESPONSE HASHPARAMS :[" & responseHashparams & "]")
	Response.Write(br & "RESPONSE HASHPARAMSVAL :[" & responseHashparamsval & "]")
	Response.Write(br & "RESPONSE HASH :[" & responseHash & "]")
        
	if (responseHashparams<> null AND  responseHashparams<>"") then
			digestData = ""
			paramList = Split(responseHashparams,":")
            paramCount = Ubound(paramList)
			Response.Write(br & "RESPONSE ParamList:")
            for i = 0 to paramCount
                param = paramList(i)
                Response.Write ("[" & param & "] value : [" & request.form(param) & "]")
                value = request.form(param)
                if(value = null) then
                   value = ""
                end if 
                digestData = digestData & value
            next			
            
			Response.Write(br & "CALCULATED digestData = ["& digestData &"]")
			hashCalculated = b64_sha1(digestData & storekey)
			Response.Write(br & "CALCULATED HASH : ["& hashCalculated &"]")
			
			if(responseHash = hashCalculated)) then 
				Response.Write(br & "!!!!!HASH VALID!!!!!")
				isValidHash = True
			else
				Response.Write(br & "!!!!!HASH INVALID!!!!!")
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

    %>

</body>
</html>