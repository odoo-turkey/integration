using System;
using System.Net;
using System.Text;
using System.IO;
using System.Xml;
using System.Collections.Generic;
using System.Linq;
using System.Web;
using System.Web.UI;
using System.Web.UI.WebControls;
using System.Security.Cryptography;

namespace $safeprojectname$
{
    public partial class _DPayResults : System.Web.UI.Page
    {

protected void Page_Load(object sender, System.EventArgs e)
{

	if (!Page.IsPostBack) {
		string strMDStatus = Request.Form.Get("mdstatus");
		string strMDStatusText = Request.Form.Get("errmsg");
		string strMDStatusText_ = Request.Form.Get("mderrormessage");
		string strResponse = Request.Form.Get("response");
		string strType = Request.Form.Get("txntype");
		string strAmount = Request.Form.Get("txnamount");
		string strInstallmentCount = Request.Form.Get("txninstallmentcount");
		string strOrderID = Request.Form.Get("oid");
		string strTerminalID = Request.Form.Get("clientid");
		string _strTerminalID = "0" + strTerminalID;
		string strStoreKey = "XXXXXXXX"; //HASH doğrulaması için 3D Secure şifreniz
		string strProvisionPassword = "XXXXXXXX"; //HASH doğrulaması için Terminal UserID şifresini tekrar yazıyoruz
		string strSuccessURL = Request.Form.Get("successurl");
		string strErrorURL = Request.Form.Get("errorurl");
		
		
//Banka tarafından gelen cevap mesajında, cevap mesajında gönderilen datalar ile bir hash değeri oluşturulup gönderilir. Üye işyerlerinin provizyon cevabında gelen bilgileri ile aynı şekilde hash değerini hesaplayarak banka tarafından gelen Hash ile aynı olup olmadığını kontrol etmelidir.  Aynı hash elde edilemiyorsa gelen mesaj üzerinde oynama olduğu ve bu mesajın banka tarafından gelmediği düşünülmelidir.  Bu durumda sanalpos ekranlarından ya da banka tarafından verilen doğrulama sorguları ile işlemlerin sanalpos tarafındaki durumu kontrol edilmelidir. 
//rnd = Hash icinde kullanılacak random deger
//hashdata = Kontrol edilmesi gereken hash değeri
//hashparams = Hash icerisinde kullanılan parametre isimleri 
//hashparamsval = Hash icerisinde kullanılan parametrelerin değerleri 
//storeKey = MPI store key 
//hashdata =  HASH(hashparamsval + storeKey)
//Hash algoritması: Base64 encoded SHA1
//HASH YAPISI 
//3D provizyon cevap mesajında  “hashparams” şeklinde bir alan dönmektedir.  
//name="hashparams" value="clientid:oid:authcode:procreturnCode:response:mdstatus:cavv:eci:md:rnd:"
//Hashparams için gerekli olan değerlerin provizyon cevabından alınarak aynı hesaplamanın 
//işyeri tarafında yapılması ve hash değerinin sanalpos üzerinden gelenle kontrol edilmesi gerekir.
//3D_Entegrasyon.doc dosyasının incelenmesini tavsiye ederiz.
//Cevap mesajındaki hash doğrulaması için örnek kod olarak ASPX3DValidation.zip dikkate alınabilir.
