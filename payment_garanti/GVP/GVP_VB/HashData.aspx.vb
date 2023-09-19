Imports System
Imports System.Net
Imports System.Security.Cryptography

Partial Public Class HashData
    Inherits System.Web.UI.Page

    Protected Sub Page_Load(ByVal sender As Object, ByVal e As System.EventArgs) Handles Me.Load
        If Not Page.IsPostBack Then
        End If
    End Sub

    Public Function GetSHA1(ByVal SHA1Data As String) As String

        Dim sha As SHA1 = New SHA1CryptoServiceProvider()
        Dim HashedPassword As String = SHA1Data
        Dim hashbytes As Byte() = Encoding.GetEncoding("ISO-8859-9").GetBytes(HashedPassword)
        Dim inputbytes As Byte() = sha.ComputeHash(hashbytes)
        Return GetHexaDecimal(inputbytes)

    End Function

    Public Shared Function GetHexaDecimal(ByVal bytes As Byte()) As String

        Dim s As New StringBuilder()
        Dim length As Integer = bytes.Length
        For n As Integer = 0 To length - 1
            s.Append([String].Format("{0,2:x}", bytes(n)).Replace(" ", "0"))
        Next
        Return s.ToString()

    End Function

    Protected Sub cmdSubmit_Click(ByVal sender As Object, ByVal e As EventArgs) Handles cmdSubmit.Click

        Dim strTerminalID As String = txtTerminalID.Text
        Dim _strTerminalID As String = "000" & txtTerminalID.Text
        Dim strProvisionPassword As String = txtPassword.Text
        Dim strOrderID As String = txtOrderID.Text
        Dim strNumber As String = txtCCNumber.Text
        Dim strAmount As String = Replace(txtAmount.Text, ",", "")

        Dim SecurityData As String = UCase(GetSHA1(strProvisionPassword + _strTerminalID))
        lblResult_SecurityData.Text = "<b>Security Data : </b>" & SecurityData

        Dim HashData As String = UCase(GetSHA1(strOrderID + strTerminalID + strNumber + strAmount + SecurityData))
        lblResult_HashData.Text = "<b>Hash Data :</b> " & HashData

    End Sub

End Class