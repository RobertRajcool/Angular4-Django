import { Component, OnInit, ViewEncapsulation } from '@angular/core';
import { FormGroup, FormBuilder, Validators } from '@angular/forms';
import { Router, ActivatedRoute, Params } from '@angular/router';
import { GetApiurl } from 'app/parameters';

import { PartnerRegistration_1, PartnerRegistration_2, PartnerRegistration_3, CoreBusinessItems, InterestedWorkLoadsItems, CustomerItems, PartnerType, PartnerDocumentType } from './partner-registration';

// Services
import { PartnerService } from './partner.service';
import { ValidationService } from 'app/directives';
import {GlobalsService} from "app/services";

declare var jQuery: any;

@Component({
  selector: 'app-partner',
  templateUrl: './partner.component.html',
  styleUrls: ['./partner.component.scss'],
  encapsulation: ViewEncapsulation.None,
})
export class PartnerComponent implements OnInit {

    partnerDocsTypes = ['image/png', 'image/jpg', 'image/jpeg', 'application/pdf', 'text/plain'];
    fileSize = 1048576;  // Equilent to 2 MB

    partnerRegistrationForm_1: FormGroup;
    partnerRegistrationForm_2: FormGroup;
    partnerRegistrationForm_3: FormGroup;
    partner_reg_1: PartnerRegistration_1 = new PartnerRegistration_1(-1, '', '', '', '', '0', '');
    partner_reg_2: PartnerRegistration_2 = new PartnerRegistration_2(-1,'', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', [], '')
    partner_reg_3: PartnerRegistration_3 = new PartnerRegistration_3(-1, [], '', '', '');
    items: any = CoreBusinessItems();
    workloadItems: any = InterestedWorkLoadsItems();
    customerItems: any = CustomerItems();
    partnerTypes: any = PartnerType();
    partnerType: Boolean = false;
    documentTypes: Array<any> = PartnerDocumentType();
    registration: string = 'progress';
    saveUsername: boolean = false;
    accountPerson: boolean = false;
    salesPerson: boolean = false;
    registered_partner_details: any;
    existing_partner_status: string = 'false';
    initial_partner_id: number = -1;
    documents_array: Array<{
        type: string,
        file: any
    }> = [];
    partner_types_array: Array<{
        id: number,
        text: string
    }> = [];

    private value: any = {};
    private customerValue: any = [];
    private workloadValue:any = [];

    bank_statement: boolean = false;
    bank_statement_file: string = 'empty';
    bank_statement_url: string = 'empty';
    income_tax: boolean = false;
    income_tax_file: string = 'empty';
    income_tax_url: string = 'empty';
    cst_lst: boolean = false;
    cst_lst_file: string = 'empty';
    cst_lst_url: string = 'empty';
    memorandum_proof: boolean = false;
    memorandum_proof_file: string = 'empty';
    memorandum_proof_url: string = 'empty';
    passport: boolean = false;
    passport_file: string = 'empty';
    passport_url: string = 'empty';
    pan_card: boolean = false;
    pan_card_file: string = 'empty';
    pan_card_url: string = 'empty';
    service_tax: boolean = false;
    service_tax_file: string = 'empty';
    service_tax_url: string = 'empty';
    agreePolicies: boolean = false;
    termsAndConditionsContent: any;
    is_customer: boolean = false;
    fileError: string = undefined;
    fileTypeError: string = undefined;

    // File validation variables
    isBsValid: string = undefined;
    isItValid: string = undefined;
    isClValid: string = undefined;
    isMpValid: string = undefined;
    isPtValid: string = undefined;
    isPaValid: string = undefined;
    isStValid: string = undefined;

    constructor(private service: PartnerService, private fb: FormBuilder, private router: ActivatedRoute, private route: Router,private gs: GlobalsService,) { }

    ngOnInit() {
        this.router.params.subscribe((params: Params) => {
                if(params['key']) {
                    this.router.queryParams.subscribe(res => {
                        if (res.hasOwnProperty('tk')) {
                            this.checkTokenExpired(res['tk'], params['key'])
                        }
                    })
                    this.getRegisteredPartnerFunc(params['key']);
                }
            });
        this.buildForm_1();
        this.buildForm_2();
        this.buildForm_3();
        let url = 'partner_terms/partner_terms_and_conditions.html';
        this.getTermsAndConditionsContent(url);
    }

    // Check customer registration token expired
    checkTokenExpired(token: string, k: string) {
        this.service.checkTokenExpired(token, k).then(res => {
            if (res) this.is_customer = true; else this.route.navigate(['error/not-found']);
        })
    }

    // Get registered partner details
    getRegisteredPartnerFunc(key: string) {
        this.service.getRegisteredPartner(key)
            .then(res => {
                if(res) {
                    this.registered_partner_details = res;
                    this.is_customer = this.registered_partner_details.customer;
                    this.mapRegistration_1();
                }
            });
    }

    // Map registration step one details function
    mapRegistration_1() {
        let contacts: Array<any> = this.registered_partner_details['initial_contacts'];
        if(this.registered_partner_details['existing_status']) {
            this.partner_reg_1.existing_partner = '1';
            this.existing_partner_status = 'true';
        } else {
            this.partner_reg_1.existing_partner = '0';
            this.existing_partner_status = 'false';
        }
        contacts.filter(element => {
            if(element.type == 'P') {
                this.partner_reg_1.name = element.name;
                this.partner_reg_1.email = element.email;
                this.partner_reg_1.mobile = element.mobile;
            }
        });
        this.partner_reg_1.company_name = this.registered_partner_details['company_name'];
        this.partner_reg_1.jba_code = this.registered_partner_details['jba_code'];
        (<FormGroup>this.partnerRegistrationForm_1).patchValue(this.partner_reg_1);
        this.initial_partner_id = this.registered_partner_details['id'];
    }

    // Map registration step two details function
    mapRegistration_2() {
        if(this.initial_partner_id != -1 && this.registered_partner_details != undefined) {
            this.mapContactDetails();
            this.mapDocumentDetails();
            this.partner_reg_2.company_name = this.registered_partner_details['company_name'];
            this.partner_reg_2.addrs_line_1 = this.registered_partner_details['address_1'];
            this.partner_reg_2.addrs_line_2 = this.registered_partner_details['address_2'];
            this.partner_reg_2.addrs_line_3 = this.registered_partner_details['address_3'];
            this.partner_reg_2.pin_code = this.registered_partner_details['pin_code'];
            this.partner_reg_2.city = this.registered_partner_details['city'];
            this.partner_reg_2.state = this.registered_partner_details['state'];
            this.partner_reg_2.preferred_user_name = this.registered_partner_details['preferred_user_name'];
            this.partner_reg_2.terms_and_cndtns_status = 'true';
            (<FormGroup>this.partnerRegistrationForm_2).patchValue(this.partner_reg_2);
        }
    }

    // Map registration step three details function
    mapRegistration_3() {
        if(this.initial_partner_id != -1 && this.registered_partner_details != undefined) {
            let partner_type_str: string = this.registered_partner_details['partner_type'];
            let focused_customer_str: string = this.registered_partner_details['focused_customer'];
            let interested_workload_str: string = this.registered_partner_details['interested_workload'];
            let core_items_array: Array<any>;
            let focused_customer: Array<any> = [];
            let interested_workloads: Array<any> = [];
            if(partner_type_str!="") this.partner_reg_3.partner_type = partner_type_str.split(',');
            for(let index of partner_type_str.split(',')) {
                if(index && index != "") {
                    this.partnerTypes[index]['checked'] = true;
                    this.partner_types_array.push({
                        'id': parseInt(this.partnerTypes[index]['id'])-1,
                        'text': this.partnerTypes[index]['symbol']
                    })
                }
            }
            if(this.registered_partner_details['business_type']!="") core_items_array= [this.items[parseInt(this.registered_partner_details['business_type'])-1]];
            this.partner_reg_3.core_business = core_items_array;
            if(focused_customer_str != null) {
                for(let i of focused_customer_str.split(',')) if(i) focused_customer.push(this.customerItems[i]);
            }
            if(focused_customer.length>0) this.partner_reg_3.focused_customer = focused_customer;
            if(interested_workload_str != null) {
                for(let i of interested_workload_str.split(',')) if(i) interested_workloads.push(this.workloadItems[i]);
            }
            if(interested_workloads.length>0) this.partner_reg_3.interested_workloads = interested_workloads;
            this.partner_reg_3.id = this.initial_partner_id;
            (<FormGroup>this.partnerRegistrationForm_3).patchValue(this.partner_reg_3);
            this.partnerType = true;
        }
    }

    // Mapping step two contact details
    mapContactDetails() {
        let contacts: Array<any> = this.registered_partner_details['initial_contacts'];
        this.partner_reg_2.director_cntct_status = 'true';
        this.partner_reg_2.accts_cntct_status = 'true';
        this.partner_reg_2.sales_cntct_status = 'true';
        this.saveUsername = true;
        this.accountPerson = true;
        this.salesPerson = true;
        contacts.filter(element => {
            if(element.type == 'D/O') {
                this.partner_reg_2.director_name = element.name;
                this.partner_reg_2.director_email = element.email;
                this.partner_reg_2.director_mobile = element.mobile;
            } else if(element.type == 'A&O') {
                this.partner_reg_2.accts_name = element.name;
                this.partner_reg_2.accts_email = element.email;
                this.partner_reg_2.accts_mobile = element.mobile;
            } else if(element.type == 'S') {
                this.partner_reg_2.sales_name = element.name;
                this.partner_reg_2.sales_email = element.email;
                this.partner_reg_2.sales_mobile = element.mobile;
            }
        });
    }

    // Mapping step two document details
    mapDocumentDetails() {
        this.partner_reg_2.documents = [];
        let document: Array<any> = this.registered_partner_details['initial_documents'];
        document.filter(file => {
            this.documentTypes.filter(element => {
                if(element.type == file['type']) {
                    if(element.symbol == 'bank_statement') {
                        this.bank_statement = true;
                        this.bank_statement_file = file['file_name'];
                        this.bank_statement_url = file['file_data'];
                    } else if(element.symbol == 'income_tax') {
                        this.income_tax = true;
                        this.income_tax_file = file['file_name'];
                        this.income_tax_url = file['file_data'];
                    } else if(element.symbol == 'cst_lst') {
                        this.cst_lst = true;
                        this.cst_lst_file = file['file_name'];
                        this.cst_lst_url = file['file_data'];
                    } else if(element.symbol == 'memorandum_proof') {
                        this.memorandum_proof = true;
                        this.memorandum_proof_file = file['file_name'];
                        this.memorandum_proof_url = file['file_data'];
                    } else if(element.symbol == 'passport') {
                        this.passport = true;
                        this.passport_file = file['file_name'];
                        this.passport_url = file['file_data'];
                    } else if(element.symbol == 'pan_card') {
                        this.pan_card = true;
                        this.pan_card_file = file['file_name'];
                        this.pan_card_url = file['file_data'];
                    } else if(element.symbol == 'service_tax') {
                        this.service_tax = true;
                        this.service_tax_file = file['file_name'];
                        this.service_tax_url = file['file_data'];
                    }
                }
            })
        })
    }

    public selected(value: any): void {
        console.log('Selected value is: ', value);
    }

    public removed(value: any): void {
        console.log('Removed value is:(): void { ', value);
    }

    public typed(value: any): void {
        console.log('New search input: ', value);
    }

    public refreshValue(value: any): void {
        this.value = value;
    }

    public customerSelected(value: any): void {
        console.log('Selected value is: ', value);
    }

    public customerRemoved(value: any): void {
        console.log('Removed value is: ', value);
    }

    public customerRefreshValue(value: any): void {
        this.customerValue = value;
    }

    public customerTyped(value: any):void {
       console.log('New search input: ', value);
    }

    public workloadSelected(value: any): void {
        console.log('Selected value is: ', value);
    }

    public workloadRemoved(value: any): void {
        console.log('Removed value is: ', value);
    }

    public workloadRefreshValue(value: any): void {
        this.workloadValue = value;
    }

    public workloadTyped(value: any):void {
       console.log('New search input: ', value);
    }

    // Form builder to bind values for partner registration step-1 screen
    buildForm_1(): void {
        this.partnerRegistrationForm_1 = this.fb.group(
            {
                'company_name' : [this.partner_reg_1.company_name, [
                    Validators.required
                ] ],
                'name' : [this.partner_reg_1.name, [
                    Validators.required
                ] ],
                'email': [this.partner_reg_1.email,[
                    Validators.required,
                    ValidationService.emailValidator
                ]],
                'mobile': [this.partner_reg_1.mobile,[
                    Validators.required,
                    ValidationService.phoneValidator
                ]],
                'existing_partner': [this.partner_reg_1.existing_partner,[
                    Validators.required
                ]],
                'jba_code': [this.partner_reg_1.jba_code]
            }
        )
    }

    // Form builder to bind values for partner registration step-2 screen
    buildForm_2(): void {
        this.partnerRegistrationForm_2 = this.fb.group(
            {
                'company_name': [this.partner_reg_2.company_name,[
                    Validators.required
                ]],
                'city': [this.partner_reg_2.city,[
                    Validators.required
                ]],
                'state': [this.partner_reg_2.state,[
                    Validators.required
                ]],
                'pin_code': [this.partner_reg_2.pin_code,[
                    Validators.required
                ]],
                'addrs_line_1': [this.partner_reg_2.addrs_line_1,[
                    Validators.required
                ]],
                'addrs_line_2': [this.partner_reg_2.addrs_line_2],
                'addrs_line_3': [this.partner_reg_2.addrs_line_3],
                'director_cntct_status': [this.partner_reg_2.director_cntct_status],
                'director_name': [this.partner_reg_2.director_name,[
                    Validators.required
                ]],
                'director_email': [this.partner_reg_2.director_email,[
                    Validators.required,
                    ValidationService.emailValidator
                ]],
                'director_mobile': [this.partner_reg_2.director_mobile,[
                    Validators.required,
                    ValidationService.phoneValidator
                ]],
                'accts_cntct_status': [this.partner_reg_2.accts_cntct_status],
                'accts_name': [this.partner_reg_2.accts_name,[
                    Validators.required
                ]],
                'accts_email': [this.partner_reg_2.accts_email,[
                    Validators.required,
                    ValidationService.emailValidator
                ]],
                'accts_mobile': [this.partner_reg_2.accts_mobile,[
                    Validators.required,
                    ValidationService.phoneValidator
                ]],
                'sales_cntct_status': [this.partner_reg_2.sales_cntct_status],
                'sales_name': [this.partner_reg_2.sales_name,[
                    Validators.required
                ]],
                'sales_email': [this.partner_reg_2.sales_email,[
                    Validators.required,
                    ValidationService.emailValidator
                ]],
                'sales_mobile': [this.partner_reg_2.sales_mobile,[
                    Validators.required,
                    ValidationService.phoneValidator
                ]],
                'preferred_user_name': [this.partner_reg_2.preferred_user_name,[
                    Validators.required,
                    ValidationService.userNameValidator
                ]],
                'gst_number': [this.partner_reg_2.gst_number],
                'terms_and_cndtns_status': [this.partner_reg_2.terms_and_cndtns_status]
            }
        )
    }

    // Form builder to bind values for partner registration step-3 screen
    buildForm_3(): void {
        this.partnerRegistrationForm_3 = this.fb.group({
            'core_business': [this.partner_reg_3.core_business,[
                Validators.required
            ]],
            'focused_customer': [this.partner_reg_3.focused_customer,[
                Validators.required
            ]],
            'interested_workloads': [this.partner_reg_3.interested_workloads,[
                Validators.required
            ]]
        })
    }

    // Checking existing partner function
    changFunc() {
        if(this.partnerRegistrationForm_1.value.existing_partner == '1') {
            this.existing_partner_status = 'true';
            this.partnerRegistrationForm_1.controls['jba_code'].setValidators([Validators.required])
            this.partnerRegistrationForm_1.controls['jba_code'].updateValueAndValidity()
        } else if(this.partnerRegistrationForm_1.value.existing_partner == '0') {
            this.existing_partner_status = 'false';
            this.partner_reg_1 = this.partnerRegistrationForm_1.value;
            this.partner_reg_1.jba_code = '';
            (<FormGroup>this.partnerRegistrationForm_1).patchValue(this.partner_reg_1);
        }
    }

    // Partner registration submit function from each step
    submitFunc(status: string) {
        if(status == 'first_step') {
            if(this.partnerRegistrationForm_1.value.existing_partner == '1') {
                if(this.partnerRegistrationForm_1.value.jba_code == '') {
                    console.log('JBA code required !');
                } else {
                    if(this.initial_partner_id == -1) {
                        this.partnerRegistration();
                    } else {
                        this.partnerRegistrationUpdate();
                        this.mapRegistration_2();
                    }
                }
            } else {
                if(this.initial_partner_id == -1) {
                    this.partnerRegistration();
                } else {
                    this.partnerRegistrationUpdate();
                    this.mapRegistration_2();
                }
            }
        } else if(status == 'second_step') {
            this.partnerRegistration_2();
            this.mapRegistration_3();
        } else if(status == 'third_step') {
            this.PartnerRegistration_3();
        }
    }

    // Partner registration function to add partner primary details to database, first step
    partnerRegistration() {
        this.service.partnerRegistration(this.partnerRegistrationForm_1.value)
                    .then(res => {
                        this.initial_partner_id = res;
                        this.partnerRegistrationForm_2.controls['company_name'].setValue(this.partnerRegistrationForm_1.value.company_name);
                    });
    }

    // Partner registration first step update process
    partnerRegistrationUpdate() {
        this.partner_reg_1 = this.partnerRegistrationForm_1.value;
        this.partner_reg_1.id = this.initial_partner_id;
        this.service.partnerRegistrationUpdate(this.partner_reg_1)
                    .then(res => {
                        this.partnerRegistrationForm_2.controls['company_name'].setValue(this.partnerRegistrationForm_1.value.company_name);
                    });
    }

    // Partner registration second step process
    partnerRegistration_2() {
        this.partner_reg_2 = this.partnerRegistrationForm_2.value;
        this.partner_reg_2.id = this.initial_partner_id;
        this.partner_reg_2.documents = this.documents_array;
        this.service.partnerRegistration_2(this.partner_reg_2);
    }

    // Partner registration third step process
    PartnerRegistration_3() {
        this.registration = 'completed';
        this.partner_reg_3 = this.partnerRegistrationForm_3.value;
        this.partner_reg_3.partner_type = this.partner_types_array;
        this.partner_reg_3.id = this.initial_partner_id;
        this.service.PartnerRegistration_3(this.partner_reg_3)
                    .then(res => {
                           jQuery('#confirmationModal').modal('show');
                           this.registration = 'progress';
                    })
    }

    // Redirect to login page when the registration completes success message receives
    backToLogin(){
        jQuery('#confirmationModal').modal('hide')
        this.route.navigateByUrl('/auth/login')
    }

    // Function to store selected documents in Array
    selectDocumentFunc(event: any, index: number, type: string) {
        event.preventDefault();
        let eventObj: MSInputMethodContext = <MSInputMethodContext> event;
        let target: HTMLInputElement = <HTMLInputElement> eventObj.target;
        let file: FileList = target.files;
        if (this.isValidFile(file)) {
            this.fileTypeError = undefined;
            this.documents_array[index] = {
                type: type,
                file: file[0]
            };
            this.setDocsVariablesValues('', type);
        } else {
            this.setDocsVariablesValues('validation', type);
        }
    }

    // Funtion to check wheather uploaded file is valid or not
    isValidFile(file: FileList) {
        if(jQuery.inArray(file[0].type, this.partnerDocsTypes) == -1) {
            this.fileError = '*Please choose a valid file';
            return false;
        } else if(file[0].size > this.fileSize) {
            this.fileError = '*Uploaded file size should be less than 2Mb';
            return false;
        } else {
            this.fileError = undefined;
            return true;
        }
    }

    // Function to remove selected documents
    removeDocumentFunc(index: number, type: string) {
        this.documents_array[index] = null;
        this.setDocsVariablesValues('', type);
    }

    // Function to set uppload document variables
    setDocsVariablesValues(docType: string, type: string) {
        if(type == 'Bank statement') {
            if(docType == 'validation') {
                this.isBsValid = this.fileError;
            } else {
                this.bank_statement_file = 'empty';
                this.bank_statement_url = 'empty';
                this.isBsValid = undefined;
            }
        } else if(type == 'Audits') {
            if(docType == 'validation') {
                this.isItValid = this.fileError;
            } else {
                this.income_tax_file = 'empty';
                this.income_tax_url = 'empty';
                this.isItValid = undefined;
            }
        } else if(type == 'CST & LST') {
            if(docType == 'validation') {
                this.isClValid = this.fileError;
            } else {
                this.cst_lst_file = 'empty';
                this.cst_lst_url = 'empty';
                this.isClValid = undefined;
            }
        } else if(type == 'Memorandum & Articles') {
            if(docType == 'validation') {
                this.isMpValid = this.fileError;
            } else {
                this.memorandum_proof_file = 'empty';
                this.memorandum_proof_url = 'empty';
                this.isMpValid = undefined;
            }
        } else if(type == 'Passport') {
            if(docType == 'validation') {
                this.isPtValid = this.fileError;
            } else {
                this.passport_file = 'empty';
                this.passport_url = 'empty';
                this.isPtValid = undefined;
            }
        } else if(type == 'Pan card') {
            if(docType == 'validation') {
                this.isPaValid = this.fileError;
            } else {
                this.pan_card_file = 'empty';
                this.pan_card_url = 'empty';
                this.isPaValid = undefined;
            }
        } else if(type == 'GST certificate') {
            if(docType == 'validation') {
                this.isStValid = this.fileError;
            } else {
                this.service_tax_file = 'empty';
                this.service_tax_url = 'empty';
                this.isStValid = undefined;
            }
        }
    }

    // Partner type choose function to add types into Array
    partnerTypeChooseFunc(event: any, type:string, index: number) {
        if(event.target.checked) {
            this.partnerType = true;
            this.partner_types_array[index] = {
                id: index,
                text: type
            }
        } else {
            this.partner_types_array.splice(index, 1);
            if(this.partner_types_array.length>0) {
                this.partnerType = true;
            } else {
                this.partnerType = false;
            }
        }
    }

    // Control terms & condition checkbox with agreePolicies
    handleSelect(event, modal: HTMLDocument) {
        if (!event.target.checked && this.agreePolicies) event.target.checked = this.agreePolicies = false;
        else {
            if (this.agreePolicies) event.target.checked = true;
            else {
                event.target.checked = false;
                jQuery(modal).modal('show');
            }
        }
    }

    getTermsAndConditionsContent(url) {
        if (url) {
            let termsAndConditionFile = GetApiurl(`uploads/` + url);
            this.service.getTermsAndConditionsContent(termsAndConditionFile).then(data => {
                this.termsAndConditionsContent = data
            });
        }

    }

}
