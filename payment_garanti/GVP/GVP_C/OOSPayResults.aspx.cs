using System;
using System.Collections;
using System.Collections.Generic;
using System.Linq;
using System.Web;
using System.Web.UI;
using System.Web.UI.WebControls;

namespace $safeprojectname$
{
    public partial class OOSPayResults : System.Web.UI.Page
    {
        protected void Page_Load(object sender, System.EventArgs e)
        {
            if (!Page.IsPostBack)
            {
                string strMDStatusText = Request.Form.Get("errmsg");
                string strResponse = Request.Form.Get("response");

                //İlk gönderilen ve bankadan dönen HASH değeri yeni üretilenle eşleşiyorsa;

                    if (strResponse == "Approved")
                    {
                        lblResults1.Text = "İşlem Başarılı";
                    }
                    else if (strResponse == "Declined")
                    {
                        lblResults1.Text = "İşlem Başarısız";
                    }

                    lblResults2.Text = strMDStatusText;

                IEnumerator f = Request.Form.GetEnumerator();
                while (f.MoveNext())
                {
                    string xkey = (string)f.Current;
                    string xval = Request.Form.Get(xkey);
                    lblResults3.Text = lblResults3.Text + (xkey + " : " + xval + "<br />");
                }
            }
        }
    }
}

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