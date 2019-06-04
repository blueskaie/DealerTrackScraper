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
        self.selectMenu("Salesmaker", "New Deal")
        self.switchMainBody()
        
        select = Select(self.browser.find_element_by_xpath(oSelYear))
        select.select_by_visible_text(year)
        
        makeOptions = self.browser.find_elements_by_xpath(oOptMake)
        make_index = 0
        make_size = len(makeOptions)
        for make_index in range(0, make_size-1):
            make_select = Select(self.browser.find_element_by_xpath(oSelMake))
            make_select.select_by_index(make_index)
            
            modelOptions = self.browser.find_elements_by_xpath(oOptModel)
            model_index = 0
            model_size = len(modelOptions)
            for model_index in range(0, model_size-1):
                model_select = Select(self.browser.find_element_by_xpath(oSelModel))
                model_select.select_by_index(model_index)

                trimOptions = self.browser.find_elements_by_xpath(oOptTrim)
                trim_index = 0
                trim_size = len(trimOptions)
                for trim_index in range(0, trim_size-1):
                    trim_select = Select(self.browser.find_element_by_xpath(oSelTrim))
                    trim_select.select_by_index(trim_index)

                    self.selectNewDealOption(year, make_index, model_index, trim_index)
                    self.selectCompareQuotes()
                    self.extractInformation()
                    self.selectMenu("Salesmaker", "New Deal")
                    self.switchMainBody()

        self.writeToCsv(year+"_result.csv")

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
            select = Select(self.browser.find_element_by_xpath(oSelMake))
            select.select_by_index(make)
            select = Select(self.browser.find_element_by_xpath(oSelModel))
            select.select_by_index(model)
            select = Select(self.browser.find_element_by_xpath(oSelTrim))
            select.select_by_index(trim)

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
            time.sleep(10)
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
            time.sleep(5)
            oChkXpath = oChkItemXpath.replace("index", str(i))
            self.clickElement(oChkXpath, str(i) + " Check Box")
            self.clickElement(oBtnWorkSheet, "WorkSheet Button")
            
            time.sleep(10)
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
            time.sleep(20)
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
            time.sleep(15)
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
        oBtnGetIncentives = "//span[@id='ucVehicle_btnRebates_lblDataLabel']"
        oTxtZipCode = "//input[@id='txtZipCode_txtTextBox']"
        oBtnRefreshIncentives = "//input[@id='btnRefreshZipCode']"
        oChk4 = "//input[@id='incGrid_dgIncentives_ctl05_chkApply']"
        oChk5 = "//input[@id='incGrid_dgIncentives_ctl06_chkApply']"
        oBtnOk = "//input[@id='btnOk']"
        oBtnCancel = "//input[@id='btnCancel']"
        oBtnCalculate = "//input[@id='btnCalculate']"        
        try:
            self.switchMainBody()
            
            #set Incentives
            # self.clickElement(oBtnGetIncentives, "GetIncentives Button")
            # time.sleep(5)
            # self.browser.find_element_by_xpath(oTxtZipCode).send_keys("92630")
            # self.clickElement(oBtnRefreshIncentives, "RefreshIncentives Button")
            # time.sleep(5)
            # self.clickElement(oChk4, "Check4")
            # self.clickElement(oChk5, "Check5")   
            # self.clickElement(oBtnOk, "OK Button")
            # time.sleep(5)

            #Click Calculate Button
            self.browser.find_element_by_xpath(oBtnCalculate).click()
            time.sleep(10)
        except:
            raise Exception("selectCompareQuotes Failure")
    
    def writeToCsv(self, filename):
        csvhelper = CsvHelper()
        csvhelper.write(filename, self.result)

def main():
    username = "zkacan"
    password = "dsrdev1#"
    c = DealerTrackScraper(username, password)
    c.run("2019")


if __name__ == "__main__":
    # call main function
    main()

