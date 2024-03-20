<?
include_once('aras.php');

$aras = new aras();
$intCode = $aras->randStr(32);


/* 	
Kullanıcı ve URL bilgileri. 
test için dev. api kullanılmıştır.
*/

$aras->UserName = "neodyum";
$aras->Password = "nd2580";
$aras->url		= "http://customerservicestest.araskargo.com.tr/arascargoservice/arascargoservice.asmx?wsdl";

/*
Sipariş bilgileri. 
*/

$aras->TradingWaybillNumber = 	"00000000";
$aras->InvoiceNumber 		= 	"12345678";
$aras->IntegrationCode		= 	$intCode;
$aras->ReceiverName			=	"Özgür Akman";
$aras->ReceiverAddress		=	"Bağlarbaşı mah. Aydın sok. no 7";
$aras->ReceiverCityName		=	"İstanbul";
$aras->ReceiverTownName		=	"Gaziosmanpaşa";
$aras->ReceiverDistrictName =	"";
$aras->ReceiverQuarterName	=	"Bağlarbaşı";
$aras->ReceiverAvenueName	=	"";
$aras->ReceiverStreetName	=	"Aydın";
$aras->ReceiverPhone1		=	"05063390181";
$aras->ReceiverPhone2		=	"";
$aras->ReceiverPhone3		=	"";
$aras->VolumetricWeight		=	"";
$aras->Weight				=	"";
$aras->CityCode				=	"";
$aras->TownCode				=	"";
$aras->SpecialField1		=	"";
$aras->SpecialField2		=	"";
$aras->SpecialField3		=	"";
$aras->IsCod				=	"1";
$aras->CodAmount			=	"500";
$aras->CodCollectionType	=	"1";
$aras->CodBillingType		=	"0";
$aras->TaxNumber			=	"";
$aras->TaxOffice			=	"";
$aras->PayorTypeCode		=	"";
$aras->IsWorldWide			=	"";
$aras->Description			=	"";

/*
Sipariş içindeki her bir parça pieces array'ı içinde tanımlanır. Bu array'in içindeki her bir parça (piece) bir objedir. Sistem uyarı vermemesi için boş bir sınıf tanımlanması yapılmıştır.
ikinci (veya 3. 4.) parçalarda da aynı şekilde bu array'in içine push edilecek objelerdir. 

*/

$aras->pieces[0] = new StdClass;
$aras->pieces[0]->VolumetricWeight = "1";
$aras->pieces[0]->Weight = "1";
$aras->pieces[0]->BarcodeNumber = $aras->randStr(32);
$aras->pieces[0]->ProductNumber = "";
$aras->pieces[0]->Description = "";

//$aras->pieces[1] = new StdClass;
//$aras->pieces[1]->VolumetricWeight = "1";
//$aras->pieces[1]->Weight = "1";
//$aras->pieces[1]->BarcodeNumber = "5063390185";
//$aras->pieces[1]->ProductNumber = "";
//$aras->pieces[1]->Description = "";



/*
Yukarıda tanımlanan değişkenler ile sipariş setOrder methodu ile tanımlanır.  Bu method sonucunda eğer çağrı başarıya ulaşmış ise sistem entegrasyon kodu ve durum bilgisi ile geri dönüş yapar.
*/

$responseSO = $aras->setOrder();
$aras->debugger($responseSO);




?>