from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utilities.CsvHelper import CsvHelper
import time
import sys

shortdelay = 2
longdelay = 5

# ************************************************************
# This is scraper for extracting data from Dealer Track Website
# *************************************************************
class DealerTrackScraper:
    
    def __init__(self, username, password):
        self.browser = webdriver.Firefox()
        self.url        = "https://login.dealertrack.com/login"
        self.username   = username
        self.password   = password
        self.header = ["Year", "Make", "Model", "Trim", "Lender", "Term", "Rebate", "Acquisition Fee", "Sales Rate", "Residual"]
        self.result = []
        self.result.append(self.header)
        self.year = ""
        self.make = ""
        self.model = ""
        self.trim = ""

    def test(self):
        self.login()
        self.selectMenu("Salesmaker", "New Deal")
        self.selectNewDealOption("2019", "Audi", "Q7")
        self.selectCompareQuotes()
        self.extractInformation()
        self.writeToCsv("result.csv")

    def run(self, year):
        oSelYear = "//select[@id='ucSelector_ddlYears']"
        oSelMake = "//select[@id='ucSelector_ddlMakes']"
        oSelModel = "//select[@id='ucSelector_ddlModels']"
        oSelTrim = "//select[@id='ucSelector_ddlTrims']"
        oOptMake = oSelMake + "/option"
        oOptModel = oSelModel + "/option"
        oOptTrim = oSelTrim + "/option"
        oBtnCompare = "//input[@id='ucSelector_btnCompareQuotes']"
        
        self.year = year
        self.login()
        time.sleep(longdelay)
        self.selectMenu("Salesmaker", "New Deal")
        time.sleep(longdelay)
        self.switchMainBody()
        
        select = Select(self.browser.find_element_by_xpath(oSelYear))
        select.select_by_visible_text(year)
        
        makeOptions = self.browser.find_elements_by_xpath(oOptMake)
        make_index = 0
        make_size = len(makeOptions)
        for make_index in range(0, make_size-1):
        # for make_index in [3,4,35]:
        # for make_index in [4]:
            try:
                make_select = Select(self.browser.find_element_by_xpath(oSelMake))
                make_select.select_by_index(make_index)
                time.sleep(longdelay)

                modelOptions = self.browser.find_elements_by_xpath(oOptModel)
                model_index = 0
                model_size = len(modelOptions)
                for model_index in range(0, model_size-1):
                # for model_index in [5]:
                    model_select = Select(self.browser.find_element_by_xpath(oSelModel))
                    model_select.select_by_index(model_index)
                    time.sleep(longdelay)

                    trimOptions = self.browser.find_elements_by_xpath(oOptTrim)
                    trim_index = 0
                    trim_size = len(trimOptions)
                    for trim_index in range(0, trim_size-1):
                        # trim_select = Select(self.browser.find_element_by_xpath(oSelTrim))
                        # trim_select.select_by_index(trim_index)
                        try:
                            self.selectNewDealOption(year, make_index, model_index, trim_index)
                            self.selectCompareQuotes()
                            self.extractInformation()
                        except:
                            pass
                        self.selectMenu("Salesmaker", "New Deal")
                        time.sleep(longdelay)
                        self.switchMainBody()
            except:
                pass
            self.writeToCsv(year+"_"+self.make+"_result.csv")


    def selectNewDealOption(self, year, make, model, trim):
        oSelYear = "//select[@id='ucSelector_ddlYears']"
        oSelMake = "//select[@id='ucSelector_ddlMakes']"
        oSelModel = "//select[@id='ucSelector_ddlModels']"
        oSelTrim = "//select[@id='ucSelector_ddlTrims']"
        oOptMake = oSelMake + "/option"
        oOptModel = oSelModel + "/option"
        oOptTrim = oSelTrim + "/option"
        oBtnCompare = "//input[@id='ucSelector_btnCompareQuotes']"
        
        try:
            self.switchMainBody()
            select = Select(self.browser.find_element_by_xpath(oSelYear))
            select.select_by_visible_text(year)
            time.sleep(shortdelay)
            select = Select(self.browser.find_element_by_xpath(oSelMake))
            select.select_by_index(make)
            time.sleep(shortdelay)
            select = Select(self.browser.find_element_by_xpath(oSelModel))
            select.select_by_index(model)
            time.sleep(shortdelay)
            select = Select(self.browser.find_element_by_xpath(oSelTrim))
            select.select_by_index(trim)
            time.sleep(shortdelay)

            oTxtMake = "(" + oOptMake + ")[" + str(make + 1) + "]"
            self.make = self.browser.find_element_by_xpath(oTxtMake).text
            oTxtModel = "(" + oOptModel + ")[" + str(model + 1) + "]"
            self.model = self.browser.find_element_by_xpath(oTxtModel).text
            oTxtTrim = "(" + oOptTrim + ")["+str(trim + 1) + "]"
            self.trim = self.browser.find_element_by_xpath(oTxtTrim).text

            print("*********************************************************************")
            print("year: " + self.year + ", make: "+self.make+", model: "+self.model+", trim: "+self.trim+"  ")
            print("*********************************************************************")

            self.clickElement(oBtnCompare, "Compare Button")
            time.sleep(longdelay)
        except:
            raise Exception("selectNewDealOption Failure")
    
    def extractInformation(self):
        oChkGenericXpath = "//img[@alt='Lease']/parent::td/preceding::td[1]/span"
        oChkItemXpath = "(//img[@alt='Lease']/parent::td/preceding::td[1]/span)[index]"
        oBtnWorkSheet = "//input[@id='btnWorksheet']"
        oTxtTerm = "//table[@id='tblPaymentCalc']//td[@id='tdcPayDepreciationTermValue']"
        oTxtRebate = "//table[@id='tblCapCost']//td[contains(.,'Rebate')]/following-sibling::td[1]"
        oTxtSalesRate = "((//table[@id='tblInterestFactor']/tbody/tr)[11]/td)[2]"
        oTxtAcqFee = "((//table[@id='tblCapCost']/tbody/tr)[14]/td)[2]"
        oTxtLender = "(//td[@id='tbTitle_tcContextCell']/table/tbody/tr)[2]/td"
        oTxtResidual = "((//table[@id='tblResidualComponents']/tbody/tr)[12]/td)[6]"
        oBtnCompare = "//input[@id='btnCQ']"

        items = self.browser.find_elements_by_xpath(oChkGenericXpath)
        size = len(items)
        for i in range(1, size):
            time.sleep(longdelay)
            oChkXpath = oChkItemXpath.replace("index", str(i))
            self.clickElement(oChkXpath, str(i) + " Check Box")
            self.clickElement(oBtnWorkSheet, "WorkSheet Button")
            
            time.sleep(longdelay)
            print("**********" + str(i) + "***********")
            row = []
            lender  = self.getText(oTxtLender, "Lender").replace("Lender Program:", "")
            term    = self.getText(oTxtTerm, "Term")
            rebate  = self.getText(oTxtRebate, "Rebate")
            acqFee  = self.getText(oTxtAcqFee, "Acquisition Fee")
            saleRate= self.getText(oTxtSalesRate, "SalesRate")
            residual= self.getText(oTxtResidual, "Residual")
            row = [self.year, self.make, self.model, self.trim, lender, term, rebate, acqFee, saleRate, residual]
            self.result.append(row)
            print("*********************************")
            self.clickElement(oBtnCompare, "Compare Button")
        time.sleep(longdelay)
           
    
    def getText(self, xpath, obj):
        result = ""
        try:
            self.browser.set_page_load_timeout(20)
            result = self.browser.find_element_by_xpath(xpath).text
        except Exception as e:
            print(e)
            pass
        print(obj + ": " + result)
        return result

    def clickElement(self, xpath, obj):
        try:
            wait = WebDriverWait(self.browser, 20)
            btn = wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
            actions = ActionChains(self.browser)
            self.browser.execute_script('arguments[0].scrollIntoView(true);', btn)
            actions.click(btn).perform()
            time.sleep(shortdelay)
            print(obj+" Clicked")
        except Exception as e:
            raise Exception("Click Error")
    
    def login(self):
        oTxtUsername    = "//input[@name='username']"
        oTxtPassword    = "//input[@name='password']"
        oBtnLogin       = "//input[@name='login']"
        try:
            self.browser.get(self.url)
            self.browser.find_element_by_xpath(oTxtUsername).send_keys(self.username)
            self.browser.find_element_by_xpath(oTxtPassword).send_keys(self.password)
            self.clickElement(oBtnLogin, "Login Button")
            time.sleep(longdelay)
        except:
            raise Exception("Login Failure")

    def selectMenu(self, mainmenu, submenu):
        oTxtIFrame = "//iframe[@id='iFrm']"
        oTxtNFrame = "//frame[@id='nav']"
        oBtnMainMenu = "//td/a[.='"+mainmenu+"']"
        oBtnSubMenu = "//td[@id='tabTD']/a[.='"+submenu+"']"
        try:
            self.browser.switch_to.default_content() 
            iframe = self.browser.find_element_by_xpath(oTxtIFrame)
            self.browser.switch_to.frame(iframe)
            nframe = self.browser.find_element_by_xpath(oTxtNFrame)
            self.browser.switch_to.frame(nframe)
            self.clickElement(oBtnMainMenu, "Main Menu "+mainmenu)
            self.clickElement(oBtnSubMenu, "Sub Menu " + submenu)
            time.sleep(longdelay)
        except:
            raise Exception("selectMenu Failure")

    def switchMainBody(self):
        oTxtIFrame = "//iframe[@id='iFrm']"
        oTxtMFrame = "//frame[@name='main']"
        try:
            self.browser.switch_to.default_content() 
            iframe = self.browser.find_element_by_xpath(oTxtIFrame)
            self.browser.switch_to.frame(iframe)
            mframe = self.browser.find_element_by_xpath(oTxtMFrame)
            self.browser.switch_to.frame(mframe)
        except:
            raise Exception("switchMainBody Failure")
    
    def selectCompareQuotes(self):
        oBtnCalculate = "//input[@id='btnCalculate']"        
        try:
            self.switchMainBody()
            self.getIncentives()
            self.clickElement(oBtnCalculate, "Calculate Button")
            time.sleep(longdelay)
        except:
            raise Exception("selectCompareQuotes Failure")
    
    def getHeaderPostion(self, header):
        oEleTh = "//div[@id='hideTableDiv']/table/thead/tr/th"
        oTxtTh = "(" + oEleTh + ")[index]"
        thlist = self.browser.find_elements_by_xpath(oEleTh)
        thsize = len(thlist)
        for index in range(1, thsize+1):
            ThXpath = oTxtTh.replace("index", str(index))
            headerName = self.browser.find_element_by_xpath(ThXpath).text
            if (headerName.find(header)>-1):
                print(header+": "+str(index))
                return index

        return -1

    def getIncentives(self):

        oBtnGetIncentives = "//span[@id='ucVehicle_btnRebates_lblDataLabel']"
        oTxtZipCode = "//input[@id='txtZipCode_txtTextBox']"
        oBtnRefreshIncentives = "//input[@id='btnRefreshZipCode']"
        oBtnOk = "//input[@id='btnOk']"
        oBtnCancel = "//input[@id='btnCancel']"

        oEleTr = "//div[@id='hideTableDiv']/table/tbody/tr/td[contains(@class,'sorting_2')]"
        oAttCheck       = "("+oEleTr+")[index]/following-sibling::td[checkpos]/input"
        oTxtProductType = "("+oEleTr+")[index]/following-sibling::td[ptypepos]"
        oTxtDetail      = "("+oEleTr+")[index]/following-sibling::td[detailpos]"

        self.clickElement(oBtnGetIncentives, "GetIncentives Button")
        time.sleep(longdelay)
        self.browser.find_element_by_xpath(oTxtZipCode).send_keys("92630")
        time.sleep(shortdelay)
        self.clickElement(oBtnRefreshIncentives, "RefreshIncentives Button")
        time.sleep(longdelay)
    
        checkPos = self.getHeaderPostion("Quote")
        ptypePos = self.getHeaderPostion("Product Type")
        detailPos = self.getHeaderPostion("Details")

        oAttCheck = oAttCheck.replace("checkpos", str(checkPos-1))
        oTxtProductType = oTxtProductType.replace("ptypepos", str(ptypePos-1))
        oTxtDetail = oTxtDetail.replace("detailpos",str(detailPos-1))

        trlist = self.browser.find_elements_by_xpath(oEleTr)
        trsize = len(trlist)
        print("********Analysis*********")
        print(trsize)
        for index in range(1, trsize+1):
            ProductTypeXpath    = oTxtProductType.replace("index", str(index))
            DetailXpath         = oTxtDetail.replace("index", str(index))
            AttCheckXpath       = oAttCheck.replace("index", str(index))
            
            pType = self.browser.find_element_by_xpath(ProductTypeXpath).text
            pDetail = self.browser.find_element_by_xpath(DetailXpath).text
            pCheck = self.browser.find_element_by_xpath(AttCheckXpath)
            pCheckValue = pCheck.get_attribute("checked")
            # print("================")
            # print(pCheckValue)
            # print(pType)
            # print(pDetail)
            # print("---------------")
            if pCheckValue is not None:
                # print("continue")
                continue
            if self.acceptableProductType(pType) is False: 
                # print("continue")
                continue
            if self.acceptableProductDetail(pDetail) is False: 
                # print("continue")
                continue
            # print("click")
            self.clickElement(AttCheckXpath, str(index)+"th Check Box")

        time.sleep(shortdelay)
        self.clickElement(oBtnOk, "OK Button")
        time.sleep(longdelay)
    
    def acceptableProductType(self, pType):
        allowProductTypes = ["All", "Lease"]
        for t in allowProductTypes:
            if pType.find(t) > -1:
                return True
        return False
    
    def acceptableProductDetail(self, pDetail):
        allowKeywords = ["Bonus", "Special Rates", "Conquest", "Acquisition", "Loyalty"]
        for d in allowKeywords:
            if pDetail.find(d) > -1:
                return True
        return False

    def writeToCsv(self, filename):
        csvhelper = CsvHelper()
        csvhelper.write(filename, self.result)

def query_yes_no(question, default="yes"):
    """Ask a yes/no question via raw_input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
        It must be "yes" (the default), "no" or None (meaning
        an answer is required of the user).

    The "answer" return value is True for "yes" or False for "no".
    """
    valid = {"yes": True, "y": True, "ye": True,
             "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "
                             "(or 'y' or 'n').\n")

def main():
    username = "zkacan"
    password = "dsrdev1#"
    
    confirm = query_yes_no("Do you want default credentials?")
    if confirm is False:
        username = input("What is your name? ")
        password = input("What is your password? ")
    year = input("What year do you want to extract?")

    c = DealerTrackScraper(username, password)
    c.run(year)

if __name__ == "__main__":
    main()

