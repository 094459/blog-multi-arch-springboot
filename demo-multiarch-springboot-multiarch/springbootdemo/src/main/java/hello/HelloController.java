package hello;
//package ricardo.sueiras.springbootdemo;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.bind.annotation.RequestMapping;

@RestController
public class HelloController {
    
    static final Logger log = LoggerFactory.getLogger(HelloController.class);
    @RequestMapping("/")
    public String index() {
        String str = "<html><head><link rel='stylesheet' href='css/style.css'><meta http-equiv='Cache-Control' content='no-cache, no-store, must-revalidate'><meta http-equiv='Pragma' content='no-cache'><meta http-equiv='Expires' content='0'></head><body>" ;
        
	    str = str.concat("<span style='color: #000000;font-family:Tahoma'><br><h1 style='text-align:center'>Multi Architecture Demo</h1>");

        str = str.concat("<p style='text-align:center;font-family:Arial'>Operating System details: ").concat(System.getProperty("os.arch")).concat(" ").concat(System.getProperty("os.name")).concat(" ").concat(System.getProperty("os.version")).concat("</p>\n");

        if (System.getenv("HOSTNAME") != null) {str = str.concat("<p style='text-align:center'>Host System details: ").concat(System.getenv("HOSTNAME")).concat("</p><br>\n");} else {str = str.concat("</p><br>\n");}

        //Display a different logo depending on the underlying architecture of the host
    
        if (System.getProperty("os.arch").contains("x86_64")) {str = str.concat("<center><img src='/images/intel.png' alt='Displaying Intel Logo' /></center>");log.info("x86 found");} else if (System.getProperty("os.arch").contains("aarch64")) {str = str.concat("<center><img src='/images/arm.png' alt='Displaying Arm Logo' /><center>");log.info("arm found");} else if (System.getProperty("os.arch").contains("amd64")) {str = str.concat("<center><img src='/images/aws.png' alt='Displaying AWS Logo' /><center>");log.info("aws found");};    

        str = str.concat("</span></body></html>");

        log.info(System.getProperty("os.arch"));
        log.info("Version v29");
        return str;
    }
    
}
