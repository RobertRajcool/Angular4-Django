import { Component, OnInit } from '@angular/core';
import { FormGroup, FormBuilder, Validators, FormControl } from '@angular/forms';
import { Subscription } from "rxjs/Rx";


import { Router, ActivatedRoute, Params } from '@angular/router';
import { CoreBusinessItems, InterestedWorkLoadsItems, CustomerItems, PartnerType } from '../../../../landing-page/partner/partner-registration';

// Services
import { PartnerService } from './../../partner.service';
import { ValidationService } from 'app/directives';

// Directives
import { Activation, Partner } from './../../partner';
import { GlobalsService } from 'app/services';
import { AuthService } from 'app/services/auth/auth.service';
@Component({
    selector: 'app-partner-details',
    templateUrl: './partner-details.component.html',
    styleUrls: ['./partner-details.component.scss']
})
export class PartnerDetailsComponent implements OnInit {

    partnerId: number;
    modalVal: any;
    private subscription: Subscription;
    private value: any = {};
    private customerValue: any = [];
    private workloadValue: any = [];
    private partnerTypeValue: any = [];
    contacts: Array<any> = [];
    partnerTypeVal: any;

    partner_type: any;
    partnerName: any;

    items: any = CoreBusinessItems();
    workloadItems: any = InterestedWorkLoadsItems();
    customerItems: any = CustomerItems();
    partnerTypes: any = PartnerType();

    show_primary_details: string;
    show_company_details: string;
    show_business_details: string;
    edit_contact: string;
    contactGroup: any = {};
    companyGroup: any = {};
    primaryContactGroup: any = {};
    businessDetailsGroup: any = {};
    partner_type_value: any;
    verificationSuccess: any;
    user_subscription: Subscription;
    userData: any;
    partner_type_values: any = [];

    partnerDetailForm: FormGroup;
    partner: Partner = new Partner(-1, '', false, -1, '', '', 0, '', '', '', '', '', '', '', 0, '', '', '', '', [], []);

    constructor(private fb: FormBuilder, private service: PartnerService, private router: ActivatedRoute, private route: Router, private gsService: GlobalsService, private authService: AuthService) {
        if (this.router.snapshot.url[0].path == 'partner-profile') {
            this.subscription = this.router.params.subscribe(
                (param: any) => {
                    let id = param['id'];
                    this.getPartnerFunc(id);
                });
        } else {
            this.subscription = this.router.parent.params.subscribe(
                (param: any) => {
                    let id = param['id'];
                    this.getPartnerFunc(id);
                });
        }
    }

    ngOnInit() {
         this.user_subscription = this.gsService.user$.subscribe(data => {
            if (data) {
                this.userData = data;
            }
        });
        this.show_company_details = 'view';
        this.show_business_details = 'view';
        this.show_primary_details = 'view';
    }

    // Get all details about the partner
    getPartnerFunc(id: number) {
        this.service.getPartnerDetail(id)
            .subscribe(data => {
                this.getValue(data);
            });
    }

    getValue(data) {
        this.partnerName = data['company_name'];
        localStorage.setItem('partner_name', this.partnerName);
        this.partner = data;
        this.partnerId = this.partner.id;
        this.contacts = this.partner.contacts;

        this.contacts.forEach((contact, index) => {
            let contact_value = this.fb.group({
                'id': [contact.id, Validators.required],
                'name': [contact.name, Validators.required],
                'email': [contact.email, [Validators.required, ValidationService.emailValidator]],
                'mobile': [contact.mobile, [Validators.required, ValidationService.phoneValidator]]
            });
            this.contactGroup[index] = contact_value;
        });

        for (var index = 0; index < this.partnerTypes.length; index++) {
            let pertnerType = this.partnerTypes[index];
            this.partnerTypes[index]['checked'] = false;
            for (let type of this.partner.partner_type.split(',')) {
                if (pertnerType['id'] == type) {
                    this.partnerTypes[index]['checked'] = true;
                }
            }
        }

        if (this.partner.focused_customer != '') {
            let focused_customers = [];
            for (let item of this.customerItems) {
                for (let type of this.partner.focused_customer.split(',')) {
                    if (item['id'] == type) {
                        focused_customers.push(item);
                    }
                }
            }
            this.partner.focused_customer = focused_customers;
        } else {
            this.partner.focused_customer = [];
        }

        if (this.partner.business_type != '') {
            let business_types = [];
            for (let item of this.items) {
                for (let type of this.partner.business_type.split(',')) {
                    if (item['id'] == type) {
                        business_types.push(item);
                    }
                }
            }
            this.partner.business_type = business_types;
        } else {
            this.partner.business_type = [];
        }

        if (this.partner.interested_workload != '') {
            let workloadItemsVal = [];
            for (let item of this.workloadItems) {
                for (let type of this.partner.interested_workload.split(',')) {
                    if (item['id'] == type) {
                        workloadItemsVal.push(item);
                    }
                }
            }
            this.partner.interested_workload = workloadItemsVal;
        } else {
            this.partner.interested_workload = [];
        }

        if (this.partner.partner_type != '') {
            this.partner_type_values = this.partnerTypes.filter(type => type.checked == true);
            let partner_types = [];
            for (let type of this.partnerTypes) {
                for (let value of this.partner.partner_type.split(',')) {
                    if (type['id'] == value) {
                        partner_types.push(type);
                    }
                }
            }
            this.partner.partner_type = this.partner_type_value = partner_types;
        } else {
            this.partner.partner_type = this.partner_type_value = [];
        }

        let formValue: any = {};
        let primary_contact_value = this.fb.group({
                'company_name': [this.partner.company_name, Validators.required],
                'city': [this.partner.city, Validators.required],
                'state': [this.partner.state, Validators.required],
                'pin_code': [this.partner.pin_code, Validators.required],
                'address_1': [this.partner.address_1, Validators.required],
                'address_2': [this.partner.address_2],
                'address_3': [this.partner.address_3]
            });
        this.primaryContactGroup[0] = primary_contact_value;

        let business_value = this.fb.group({
                'business_type': [this.partner.business_type, Validators.required],
                'focused_customer': [this.partner.focused_customer, Validators.required],
                'partner_type': [this.partner.partner_type],
                'interested_workload': [this.partner.interested_workload, Validators.required],
                'gst_number': [this.partner.gst_number]
            });
        this.businessDetailsGroup[0] = business_value;

        let company_value = this.fb.group({
                'name': [this.partner.name, Validators.required],
                'contact_id': [this.partner.contact_id, Validators.required],
                'email': [this.partner.email, Validators.required],
                'mobile': [this.partner.mobile, Validators.required],
                'jba_code': [this.partner.jba_code, Validators.required]
            });
        this.companyGroup[0] = company_value;

        formValue['id'] = new FormControl(this.partner.id, Validators.required);
        formValue['status'] = new FormControl(this.partner.status, Validators.required);
        formValue['credits'] = new FormControl(this.partner.credits, Validators.required);
        formValue['activated_by'] = new FormControl(this.partner.activated_by);
        formValue['vendor_list'] = new FormControl(this.partner.vendor_list);
        formValue['companyGroup'] = new FormGroup(this.companyGroup);
        formValue['contactGroup'] = new FormGroup(this.contactGroup);
        formValue['primaryContactGroup'] = new FormGroup(this.primaryContactGroup);
        formValue['businessDetailsGroup'] = new FormGroup(this.businessDetailsGroup);

        this.partnerDetailForm = new FormGroup(formValue);
    }

    submitForm(f) {
        console.log(f);
        this.partner = this.partnerDetailForm.value;
        this.partner.id = this.partnerId;

        // company details
        this.partner.name = this.partnerDetailForm.value.companyGroup[0].name;
        this.partner.contact_id = this.partnerDetailForm.value.companyGroup[0].contact_id;
        this.partner.email = this.partnerDetailForm.value.companyGroup[0].email;
        this.partner.mobile = this.partnerDetailForm.value.companyGroup[0].mobile;
        this.partner.jba_code = this.partnerDetailForm.value.companyGroup[0].jba_code;

        // Primary contact details
        this.partner.company_name = this.partnerDetailForm.value.primaryContactGroup[0].company_name;
        this.partner.address_1 = this.partnerDetailForm.value.primaryContactGroup[0].address_1;
        this.partner.address_2 = this.partnerDetailForm.value.primaryContactGroup[0].address_2;
        this.partner.address_3 = this.partnerDetailForm.value.primaryContactGroup[0].address_3;
        this.partner.city = this.partnerDetailForm.value.primaryContactGroup[0].city;
        this.partner.state = this.partnerDetailForm.value.primaryContactGroup[0].state;
        this.partner.pin_code = this.partnerDetailForm.value.primaryContactGroup[0].pin_code;

        // Business details
        this.partner.business_type = this.partnerDetailForm.value.businessDetailsGroup[0].business_type;
        this.partner.focused_customer = this.partnerDetailForm.value.businessDetailsGroup[0].focused_customer;
        this.partner.interested_workload = this.partnerDetailForm.value.businessDetailsGroup[0].interested_workload;
        this.partner.partner_type = this.partnerTypes;
        this.partner.gst_number = this.partnerDetailForm.value.businessDetailsGroup[0].gst_number;

        this.service.updatePartner(this.partner)
            .subscribe(data => {
                this.show_company_details = 'view';
                this.show_business_details = 'view';
                this.show_primary_details = 'view';
                this.edit_contact = null;
                this.getValue(data);
            });
    }

    public selected(value: any): void {
        // console.log('Selected value is: ', value);
    }

    public removed(value: any): void {
        // console.log('Removed value is:(): void { ', value);
    }

    public typed(value: any): void {
        // console.log('New search input: ', value);
    }

    public refreshValue(value: any): void {
        this.value = value;
    }

    public customerSelected(value: any): void {
        // console.log('Selected value is: ', value);
    }

    public customerRemoved(value: any): void {
        // console.log('Removed value is: ', value);
    }

    public customerRefreshValue(value: any): void {
        this.customerValue = value;
    }

    public workloadSelected(value: any): void {
        // console.log('Selected value is: ', value);
    }

    public workloadRemoved(value: any): void {
        // console.log('Removed value is: ', value);
    }

    public partnerTypeRefreshValue(value: any): void {
        this.customerValue = value;
    }

    public partnerTypeSelected(value: any): void {
        // console.log('Selected value is: ', value);
    }

    public partnerTypeRemoved(value: any): void {
        // console.log('Removed value is: ', value);
    }

    public workloadRefreshValue(value: any): void {
        this.partnerTypeValue = value;
    }

    handleSelect(event): void {

        let optionIndex = this.partnerTypes.map((partnerType) => partnerType['id']).indexOf(parseInt(event.target.value));

        if (event.target.checked) {
            this.partnerTypes[optionIndex]['checked'] = true;
        } else {
            this.partnerTypes[optionIndex]['checked'] = false;
        }
        this.partner_type_values = this.partnerTypes.filter(type => type.checked == true);

        this.partner.partner_type = this.partnerTypes;
    }
    showPrimaryDetails(type) {
        if (type == 'edit') {
            this.show_primary_details = 'edit'
        } else {
            this.show_primary_details = 'view'
        }
        (<FormGroup>this.partnerDetailForm).patchValue(this.partner);
    }

    showCompanyDetails(type) {
        if (type == 'edit') {
            this.show_company_details = 'edit'
        } else {
            this.show_company_details = 'view'
        }
        (<FormGroup>this.partnerDetailForm).patchValue(this.partner);
    }
    showBusinessDetails(type) {
        if (type == 'edit') {
            this.show_business_details = 'edit'
        } else {
            this.show_business_details = 'view'
        }
        if (type != 'edit') {
            this.partner.partner_type = this.partner_type_value;
            this.getPartnerTypeValue(this.partner);
            (<FormGroup>this.partnerDetailForm).patchValue(this.partner);
        }
    }
    showContactDetails(contact, index, type) {
        if(type == 'edit') {
            this.edit_contact = contact.type;
        } else {
            this.edit_contact = null;
        }

        (<FormGroup>this.partnerDetailForm).patchValue(this.partner);
        (<FormGroup>this.partnerDetailForm.controls['contactGroup']['controls'][index]).patchValue(contact);
    }
    getPartnerTypeValue(partner){
        for (var index = 0; index < this.partnerTypes.length; index++) {
            let pertnerType = this.partnerTypes[index];
            this.partnerTypes[index]['checked'] = false;
            for (let type of partner.partner_type) {
                if (pertnerType['id'] == type['id']) {
                    this.partnerTypes[index]['checked'] = true;
                }
            }
        }
    }

    resetPassword(partner) {
        let userName = partner.user_name;
        let email = partner.email;
        this.authService
                .generatePasswordResetLink(userName, email)
                .subscribe(
                Result => {
                    this.verificationSuccess = Result;
                    this.gsService.setToastMessage('Link to reset password has been sent to ' + this.verificationSuccess['email'], 3000);
                });
    }
}
