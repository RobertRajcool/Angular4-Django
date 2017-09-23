import { Component, OnInit, OnDestroy } from '@angular/core';
import { FormBuilder, FormGroup, Validators, AbstractControl } from "@angular/forms";
import { Router, ActivatedRoute, NavigationExtras } from "@angular/router";
import { CustomersService } from 'app/services/customers.service';
import { PartnerService } from 'app/portal/partner/partner.service';
import { GetValidimageTypes, cloudVendors } from 'app/parameters';
import { Subscription } from 'rxjs/Subscription';
import { ValidationService } from "../../../directives/form-validations/validation.service";
import { VendorService } from 'app/services';
import { CustomerItems } from '../../../landing-page/partner/partner-registration';
import { Angulartics2 } from 'angulartics2';

@Component({
    selector: 'app-add',
    templateUrl: './add.component.html',
    styleUrls: ['./add.component.scss']
})
export class AddComponent implements OnInit {
    private addCustomerForm: FormGroup;
    private logoError: string;
    private imageFileName: string;
    private imageFile: any;
    private routerUrl: any;
    private subscription: Subscription;
    private partnerId: number;
    invalid_domain: boolean = false;
    partnerObject: any;
    returnPath: string = '/app/customers';
    routeQueryParamsSubscription: Subscription;
    process: string;
    needCloudAccount: boolean = false;
    additionalRequirements: {
        titles: Array<string>;
        cloud_account?: {
            validations: Object;
            account_type: Array<string>;
            account_exists: boolean;
            state: string;
        },
        datas?: Object;
    } = {
        titles: [],
        datas: {}
    };
    customerItems: any = CustomerItems();
    private customerValue: any = [];
    public customerDeliverySequence = [];
    deliverySequenceItems
    public segmentItems=['SMB','Non-SMB']

    constructor(
        private fb: FormBuilder,
        private router: Router,
        private cs: CustomersService,
        private ps: PartnerService,
        private route: ActivatedRoute,
        private vendorService: VendorService,
        private angulartics2: Angulartics2
    ) {
        this.routerUrl = router['url'];
        this.subscription = this.route.params.subscribe(
            (param: any) => {
                let id = param['id'];
                this.partnerId = id;
            })
    }

    ngOnInit() {

        if (this.partnerId > 0) {
            this.ps.getPartnerDetail(this.partnerId).subscribe(partner => {
                this.returnPath = `/app/partner/${partner['id']}/customers`;
                this.partnerObject = partner;
            });
        }
        this.getDeliverySequence()

        this.addCustomerForm = this.fb.group({
            'company_name': ['', [Validators.required]],
            'logo': [''],
            'address': ['', [Validators.required]],
            'postcode': ['', [Validators.required]],
            'city': ['', [Validators.required]],
            'state': ['', [Validators.required]],
            'country': ['India', [Validators.required]],
            'pan_number': [''],
            'contact_name': ['', [Validators.required]],
            'position': [''],
            'email': ['', [Validators.required, ValidationService.emailValidator]],
            'mobile': ['', [Validators.required, ValidationService.phoneValidator]],
            'optional_contact_name': [''],
            'optional_contact_position': [''],
            'optional_contact_email': [''],
            'optional_contact_mobile': [''],
            'customer_vertical': ['', [Validators.required]],
            'delivery_sequence':['',[Validators.required]],
            'segment':['',[Validators.required]]
        });

        // Subscribing query params and forming return url
        this.routeQueryParamsSubscription = this.route.queryParams.subscribe(params => {
            if (Object.keys(params).indexOf('mode') >= 0) {
                // constructing return path
                if ((params['mode'] == 'return') && (params['target'] == 'market')) {
                    this.returnPath = `/app/market-place`;
                }

                // checking for extra informations
                if (Object.keys(params).indexOf('extra') >= 0)
                    this.configureAdditionalRequirements(params);
            }
        });
    }

     getDeliverySequence(){
        let customer=''
        this.cs.deliverySequence(customer)
       .then(data => {
        this.deliverySequenceItems =data
         if (data.length!=0){
            this.deliverySequenceItems =data
         }
         else{
           this.deliverySequenceItems=[{'dDSEQ':'000'}]
         }
      })

     }


    saveCustomer() {
        this.invalid_domain = false;
        this.process = 'saving';
        let customerData = {
            'company_name': this.addCustomerForm.controls['company_name'].value,
            'logo': this.imageFile,
            'address': this.addCustomerForm.controls['address'].value,
            'city': this.addCustomerForm.controls['city'].value,
            'postcode': this.addCustomerForm.controls['postcode'].value,
            'state': this.addCustomerForm.controls['state'].value,
            'country': this.addCustomerForm.controls['country'].value,
            'pan_number': this.addCustomerForm.controls['pan_number'].value,
            'customer_vertical': this.addCustomerForm.controls['customer_vertical'].value,
            'partner_id': this.partnerId,
            'delivery_sequence':this.addCustomerForm.controls['delivery_sequence'].value,
            'segment':this.addCustomerForm.controls['segment'].value,

            'primary_contact': {
                'name': this.addCustomerForm.controls['contact_name'].value,
                'position': this.addCustomerForm.controls['position'].value,
                'email': this.addCustomerForm.controls['email'].value,
                'mobile': this.addCustomerForm.controls['mobile'].value,
            },
            'secondary_contact': {
                'name': this.addCustomerForm.controls['optional_contact_name'].value,
                'position': this.addCustomerForm.controls['optional_contact_position'].value,
                'email': this.addCustomerForm.controls['optional_contact_email'].value,
                'mobile': this.addCustomerForm.controls['optional_contact_mobile'].value,
            }
        };

        // Additional requirements data
        if (this.additionalRequirements.titles.length > 0) {
            this.additionalRequirements.titles.forEach(title => {
                if (Object.keys(this.addCustomerForm.value).indexOf(title) >= 0) customerData[title] = this.addCustomerForm.value[title];
            });
        }

        this.cs.createCustomer(customerData, this.imageFile)
            .then(data => {
                this.process = '';

                // For Google Analytics
                this.angulartics2.eventTrack.next({
                    action: 'Created',
                    properties: {
                        category: 'Customers'
                    }
                });

                if (data == 'Invalid_domain') {
                    this.invalid_domain = true;
                    return;
                }
                if (this.routerUrl == '/app/partner/' + this.partnerId + '/add_customer') {
                    this.router.navigate(['/app/partner/' + this.partnerId + '/customers']);
                } else if (this.returnPath == '/app/market-place') {
                    let navExtras: NavigationExtras = {
                        queryParams: { 'customer_id': data }
                    }
                    this.router.navigate([this.returnPath], navExtras);
                } else {
                    this.router.navigate([this.returnPath]);
                }
            });
    }

    private previewFile(aggrementFile) {
        var reader = new FileReader();
        let previewElement = jQuery('#vendorlogoid')
        reader.addEventListener("load", function (e) {
            previewElement.attr('src', reader.result);
        }, false);

        if (aggrementFile) {
            reader.readAsDataURL(aggrementFile[0]);
        }
    }

    private openImageFile(event) {
        event.preventDefault();
        jQuery('#imageFile').click();
    }

    private uploadImageFile(event) {
        event.preventDefault();
        let eventObj: MSInputMethodContext = <MSInputMethodContext> event;
        let target: HTMLInputElement = <HTMLInputElement> eventObj.target;
        let imageFile: FileList = target.files;
        let imageFileName = imageFile[0].name;
        let imageFileSize = imageFile[0].size;
        let fileType = imageFile[0].type
        let validImageTypesandSize = GetValidimageTypes();
        if (jQuery.inArray(fileType, validImageTypesandSize.validType) == -1) {
            this.logoError = 'Please upload an image file'
            this.imageFileName = null
            jQuery('#vendorlogoid').attr('src', './../../../assets/img/noimage.jpg');
        } else if (imageFileSize > validImageTypesandSize.validSize) {
            this.logoError = 'Please upload a file less than 1MB';
            this.imageFileName = null
            jQuery('#vendorlogoid').attr('src', './../../../assets/img/noimage.jpg');
        } else {
            this.imageFile = imageFile[0];
            this.logoError = null;
            this.imageFileName = imageFileName;
            this.previewFile(imageFile);
        }

    }

    private Back() {
        if (this.routerUrl == '/app/partner/' + this.partnerId + '/add_customer') {
            this.router.navigate(['/app/partner/' + this.partnerId + '/customers']);
        }
        else {
            this.router.navigate(['/app/customers/list'])
        }
    }

    // Configuring customer addional information requirements forms
    configureAdditionalRequirements(params: Object) {
        let titles: Array<string> = decodeURIComponent(params['extra']).split(',');
        this.additionalRequirements.titles = titles;

        // Generating customer's cloud account form
        if (titles.indexOf('cloud_account') >= 0) {
            let validations = {
                'customer': [],
                'vendor': [Validators.required],
                'type': [Validators.required],
                'active': [Validators.required],
                'account_id': [Validators.required],
                'preferred_username': [Validators.required],
                'domain_name': [Validators.required],
                'customer_vertical': [Validators.required]
            };

            this.additionalRequirements.cloud_account = {
                validations: validations,
                account_type: [null, null],
                account_exists: false,
                state: 'questing'
            }

            let form = this.fb.group({
                'customer': ['', validations['customer']],
                'vendor': ['', validations['vendor']],
                'type': ['', validations['type']],
                'details': this.fb.group({
                    'account_id': [''],
                    'preferred_username': [''],
                    'domain_name': ['']
                }),
                'active': [false, validations['active']],
                'customer_vertical': ['', validations['customer_vertical']],
            });

            // Registering cloud account requirements form to add customer form
            this.addCustomerForm.registerControl('cloud_account', form);

            // Fetch vendor details from server
            this.vendorService
                .fetchVendor({ 'vendor_name': params['vendor'] })
                .subscribe(
                Result => {
                    this.additionalRequirements.datas['vendor_details'] = Result;
                    let cloudVendorLabels: Array<string> = cloudVendors.map(element => element[1]);
                    let cloudVendor: Array<string> = cloudVendors[cloudVendorLabels.indexOf(Result['vendor_name'])]
                    this.additionalRequirements.cloud_account.account_type = cloudVendor;
                    // Updating vendor value on cloud account form
                    this.configureFormControls(
                        [
                            ['vendor', Result['vendor_id'], true, true],
                            ['type', cloudVendor[0], true, true]
                        ],
                        this.addCustomerForm.get('cloud_account'),
                        this.additionalRequirements.cloud_account.validations
                    );
                });
        }
    }

    // Preparing cloud account form
    prepareCloudAccountForm(existing: boolean) {
        this.additionalRequirements.cloud_account.account_exists = existing;
        this.additionalRequirements.cloud_account.state = 'data_entry';
        let form = this.addCustomerForm.get('cloud_account');
        let validations = this.additionalRequirements.cloud_account.validations;

        // Configure for existing accounts
        if (existing) {
            this.configureFormControls([['active', true, true, true]], form, validations);

            // Prepare for AWS account
            if (this.additionalRequirements.cloud_account.account_type[0] == 'AWS') {
                this.configureFormControls([
                    ['preferred_username', '', false, true],
                    ['account_id', '', true, true],
                    ['domain_name', '', false, false],
                ], form['controls']['details'], validations);
            }
            // Prepare for Microsoft account
            else if (this.additionalRequirements.cloud_account.account_type[0] == 'MS') {
                this.configureFormControls([
                    ['preferred_username', '', false, false],
                    ['account_id', '', false, false],
                    ['domain_name', '', true, true],
                ], form['controls']['details'], validations);
            }

        }
        // Configure for non existing accounts
        else {
            this.configureFormControls([['active', false, true, true]], form, validations);

            // Prepare for AWS account
            if (this.additionalRequirements.cloud_account.account_type[0] == 'AWS') {
                this.configureFormControls([
                    ['preferred_username', '', true, true],
                    ['account_id', '', false, true],
                    ['domain_name', '', false, false],
                ], form['controls']['details'], validations);
            }
            // Prepare for Microsoft account
            else if (this.additionalRequirements.cloud_account.account_type[0] == 'MS') {
                this.configureFormControls([
                    ['preferred_username', '', false, false],
                    ['account_id', '', false, false],
                    ['domain_name', '', false, true],
                ], form['controls']['details'], validations);
            }
        }
    }

    // Assigning values and validations for form controls
    configureFormControls(properties: Array<Array<any>>, formGroup: any, validations: Object) {

        properties.forEach(property => {
            // Set value
            formGroup.controls[property[0]].setValue(property[1]);
            // Set or Unset validations
            if (property[2]) formGroup.controls[property[0]].setValidators(validations[property[0]]);
            else formGroup.controls[property[0]].setValidators(null);

            // Enable or Disable form controls
            if (property[3]) formGroup.controls[property[0]].enable();
            else formGroup.controls[property[0]].disable();

            formGroup.controls[property[0]].updateValueAndValidity();
        });
    }

    ngOnDestroy() {
        this.routeQueryParamsSubscription.unsubscribe();
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

    public customerTyped(value: any): void {
        console.log('New search input: ', value);
    }
}
