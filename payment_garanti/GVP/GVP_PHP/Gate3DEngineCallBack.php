/*3D Dönen Hash deðeri kontrol eder*7
    
    function hash_data($result,$responseHashparams,$responseHash)
    
    {
            $isValidHash = false;
            $storekey="********"; 
            
            if ($responseHashparams!==NULL &&  $responseHashparams!=="")
            {
                    $digestData = "";
                    $paramList = explode(":", $responseHashparams);
                    
                    foreach ($paramList as $param)
                    {
                       
                        $value= $result[strtolower($param)];
                        
                        if($value==null)
                        {
                            $value="";
                        }
                        
                        $digestData .= $value;
                    }
                    
                    $digestData .= $storekey;
                    $hashCalculated = base64_encode(pack('H*',sha1($digestData)));
                    
                    if($responseHash==$hashCalculated)
                    {
                        $isValidHash = true;
                    }
                    
                    
            }
            
            return $isValidHash;
    }

/*Bu class a gönderilen veriler de aþaðýdaki gibi hazýrlanýr ...*/
/*   $responseHashparams = $_POST["hashparams"]; */
/*   $responseHash = $_POST["hash"]; */
/*   $result = $_POST; */
/*   $hash_valid = $class_adi-> hash_data( $result,$responseHashparams,$responseHash ); */
/*   $hash_valid deðeri true dönerse hash deðeri doðrudur, false dönerse yanlýþtýr ... */

