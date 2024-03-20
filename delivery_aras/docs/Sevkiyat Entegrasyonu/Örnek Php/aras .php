<?

/*****
Aras Class w/o barcode
Brandwolf
28.12.2016
*****/

class aras {	
	function order() {
		$return = array(
			"UserName"					=> 	$this->UserName,
			"Password" 					=>	$this->Password,
			"TradingWaybillNumber"		=>	$this->TradingWaybillNumber,
			"InvoiceNumber"				=>	$this->InvoiceNumber,
			"IntegrationCode"			=>	$this->IntegrationCode,
			"ReceiverName"				=>	$this->ReceiverName,
			"ReceiverAddress"			=>	$this->ReceiverAddress,
			"ReceiverCityName"			=>	$this->ReceiverCityName,
			"ReceiverTownName"			=>	$this->ReceiverTownName,
			"ReceiverDistrictName"		=>	$this->ReceiverDistrictName,
			"ReceiverQuarterName"		=>	$this->ReceiverQuarterName,
			"ReceiverAvenueName"		=>	$this->ReceiverAvenueName,
			"ReceiverStreetName"		=>	$this->ReceiverStreetName,
			"ReceiverPhone1"			=>	$this->ReceiverPhone1,
			"ReceiverPhone2"			=>	$this->ReceiverPhone2,
			"ReceiverPhone3"			=>	$this->ReceiverPhone3,
			"VolumetricWeight"			=>	$this->VolumetricWeight,
			"Weight"					=>	$this->Weight,
			"CityCode"					=>	$this->CityCode,
			"TownCode"					=>	$this->TownCode,
			"SpecialField1"				=>	$this->SpecialField1,
			"SpecialField2"				=>	$this->SpecialField2,
			"SpecialField3"				=>	$this->SpecialField3,
			"IsCod"						=>	$this->IsCod,
			"CodAmount"					=>	$this->CodAmount,
			"CodCollectionType"			=>	$this->CodCollectionType,
			"CodBillingType"			=>	$this->CodBillingType,
			"TaxNumber"					=>	$this->TaxNumber,
			"TaxOffice"					=>	$this->TaxOffice,
			"PayorTypeCode"				=>	$this->PayorTypeCode,
			"IsWorldWide"				=>	$this->IsWorldWide,
			"Description"				=>	$this->Description,
		);
		if ($this->pieces) {
			$return["PieceDetails"]	 	= 	$this->PieceDetails();
			$return["PieceCount"]		=	count($this->PieceDetails());
		}
		return $return;
	}

	function PieceDetails() {
		foreach ($this->pieces as $piece) {
				$return[] = array(
				"VolumetricWeight"			=>$piece->VolumetricWeight,
				"Weight"					=>$piece->Weight,
				"BarcodeNumber"				=>$piece->BarcodeNumber,
				"ProductNumber"				=>$piece->ProductNumber,
				"Description"				=>$piece->Description,
			);
		}
		return $return;
	}

	function setOrder() {
		try {
			$client = new SoapClient($this->url, array("encoding"=>"UTF-8"));
			$response=$client->SetOrder(array("orderInfo"=>array("Order"=>$this->order()),"userName"=>$this->UserName,"password"=>$this->Password));
			$return = (array) $response->SetOrderResult->OrderResultInfo;

		} catch (Exception $exc) {
			$return = $exc->getMessage();
		}

		return $return;
	}


	function randStr($length = 10) {
		$str = "";
		$characters = array_merge(range('A','Z'), range('a','z'), range('0','9'));
		$max = count($characters) - 1;
		for ($i = 0; $i < $length; $i++) {
			$rand = mt_rand(0, $max);
			$str .= $characters[$rand];
		}
		return $str;
	}

	/* Debugging */
	function debugger($array){
	    echo '<pre>';
	    print_r($array);
	    echo '</pre>';
	}
}

?>