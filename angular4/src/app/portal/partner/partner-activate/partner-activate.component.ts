import { Component, OnInit } from '@angular/core';
import { Router, ActivatedRoute, Params } from '@angular/router';
import { FormGroup, FormBuilder, Validators } from '@angular/forms';

// Services
import { InactivePartnerService } from './../../inactive-partner/inactive-partner.service';

// Directives
import { Select2OptionData } from 'ng2-select2/ng2-select2';
import { Activation, Rejection, Partner } from './../partner';
import { InterestedWorkLoadsItems, CoreBusinessItems, CustomerItems, PartnerType } from '../../../landing-page/partner/partner-registration';
import { Modal } from 'ng2-modal';

@Component({
  selector: 'app-partner-activate',
  templateUrl: './partner-activate.component.html',
  styleUrls: ['./partner-activate.component.scss']
})
export class PartnerActivateComponent implements OnInit {

    rejection_reason: string = '';
    scrn_var: string;
    selectedVal: any;
    modalVal: any;
    activation_id: number;
    process_status: string = 'progress';
    partner: Partner = new Partner(-1,'',false,-1,'','',0,'','','','','','','',0,'','','','',[],[]);
    businessItems: any = CoreBusinessItems();
    workloadItems: any = InterestedWorkLoadsItems();
    customerItems: any = CustomerItems();
    partnerType: any = PartnerType();
    partnerActivationForm: FormGroup;
    partnerActivation: Activation = new Activation(0, '0', '', 300000, '');
    partnerRejectionForm: FormGroup;
    partnerRejection = new Rejection(-1, '');
    isValidUser: string = undefined;
    isValidCode: string = undefined;
    isCustomer: boolean = false;

    select2Options: any = {
        theme: 'bootstrap'
    };

    select2DefaultData: Array<any> = [
        { id: 1, text: 'Not Existing' },
        { id: 2, text: 'Existing' }
    ]

    constructor(private service: InactivePartnerService, private router: ActivatedRoute, private fb: FormBuilder, private route: Router) {}

    ngOnInit() {
        this.router.params.subscribe((params: Params) => {
                this.getPartnerFunc(params['id']);
            });
        this.buildForm();
        this.rejectionForm();
    }

    // Get all details about the partner
    getPartnerFunc(id: number) {
        this.service.getInactivePartner(id)
            .then(data => {
                this.isCustomer = data.customer;
                this.extractPartnerFunc(data);
                localStorage.setItem('partner_name', data['company_name'])
                this.partnerActivation.preferred_user_name = data.preferred_user_name;
                this.partnerActivation.jba_code = data.jba_code;
                if(data.existing_status) {
                    this.partnerActivation.existing_status = '1';
                } else {
                    this.partnerActivation.existing_status = '0';
                }
                this.activation_id = data.id;
                (<FormGroup>this.partnerActivationForm).patchValue(this.partnerActivation);
            });
    }

    // Mapping partner data function
    extractPartnerFunc(data: any) {
        this.partner.id = data['id'];
        this.partner.company_name = data['company_name'];
        this.partner.pin_code = data['pin_code'];
        this.partner.state = data['state'];
        this.partner.city = data['city'];
        this.partner.address_1 = data['address_1'];
        this.partner.address_2 = data['address_2'];
        this.partner.business_type = this.businessItems[parseInt(data['business_type'])-1]['text'];
        this.mapContactDetails(data['initial_contacts']);
        this.mapInterestedWorkLoads(data['interested_workload']);
        this.mapFocusedCustomers(data['focused_customer']);
        this.mapPartnerType(data['partner_type']);
        this.partner.documents = data['initial_documents'];
        this.partner.gst_number = data['gst_number'];
    }

    // Mapping primary contact details
    mapContactDetails(data: Array<any>) {
        data.filter(element => {
            if(element.type == 'P'){
                this.partner.name = element.name;
                this.partner.email = element.email;
                this.partner.mobile = element.mobile;
            } else {
                this.partner.contacts.push(element);
            }
        });
    }

    // Mapping interested workload items
    mapInterestedWorkLoads(items: string) {
        let item_array: Array<string> = [];
        items.split(',').forEach(item => {
            item_array.push(this.workloadItems[parseInt(item)-1]['text']);
        });
        this.partner.interested_workload = item_array;
    }

    // Mapping focused customers
    mapFocusedCustomers(customers: string) {
        let customer_array: Array<string> = [];
        customers.split(',').forEach(customer => {
            customer_array.push(this.customerItems[parseInt(customer)-1]['text']);
        });
        this.partner.focused_customer = customer_array;
    }

    // Mapping partner types
    mapPartnerType(types: string) {
        let type_array: Array<string> = [];
        types.split(',').forEach(type => {
            if(type != '') {
                type_array.push(this.partnerType[parseInt(type)]['text']);
            }
        });
        this.partner.partner_type = type_array;
    }

    // Form builder to bind values for partner activation
    buildForm(): void {
        this.partnerActivationForm = this.fb.group(
            {
                'existing_status': [this.partnerActivation.existing_status],
                'jba_code': [this.partnerActivation.jba_code,[
                    Validators.required
                ]],
                'credits': [this.partnerActivation.credits,[
                    Validators.required
                ]],
                'preferred_user_name': [this.partnerActivation.preferred_user_name, [
                    Validators.required
                ]]
            }
        )
    }

    // Rejection form builder to bind values
    rejectionForm(): void {
        this.partnerRejectionForm = this.fb.group(
            {
                'rejection_reason': [this.partnerRejection.rejection_reason, [
                    Validators.required
                ]]
            }
        )
    }

    getSelect2DefaultList() {
         return this.select2DefaultData;
     }

    select2Changed(e: any): void {
        this.selectedVal = e.value;
    }

    // Activate function to activate the partner
    activatePartnerFunc(f) {
        this.process_status = "activating";
        this.partnerActivation = this.partnerActivationForm.value;
        this.partnerActivation.id = this.activation_id;
        if(this.activation_id != undefined) {
            this.service.checkUserName(this.partnerActivation)
                .then(res => {
                    if(res == true) {
                        this.isValidUser = undefined;
                        this.service.checkDealerCode(this.partnerActivation)
                            .then(dealer => {
                                if(dealer == true) {
                                    this.isValidCode = undefined;
                                    this.service.partnerActivation(this.partnerActivation)
                                        .then(res => {
                                            this.process_status = "progress";
                                            if (this.isCustomer) {
                                                this.route.navigateByUrl("/app/partner-customers/inactive");
                                            } else {
                                                this.route.navigateByUrl("/app/inactive-partner");
                                            }
                                        })
                                } else {
                                    this.process_status = "progress";
                                    this.isValidCode = 'Dealer code already exists !';
                                }
                            })
                    } else if(res == false) {
                        this.process_status = "progress";
                        this.isValidUser = 'Username already exists !';
                    }
                });
        } else {
            this.process_status = "progress";
        }
    }

    // Partner reject function
    rejectPartnerFunc() {
        this.process_status = "rejecting";
        this.partnerRejection = this.partnerRejectionForm.value;
        this.partnerRejection.id = this.activation_id;
        if(this.activation_id != undefined) {
            this.service.partnerRejection(this.partnerRejection)
                .then(res => {
                    this.route.navigateByUrl("/app/inactive-partner");
                    this.process_status = "progress";
                });
        } else {
            this.process_status = "progress";
        }
    }

    eventListener(event: any): void {
        this.scrn_var = '';
    }
}
