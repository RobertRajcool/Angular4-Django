import { Component, OnInit } from '@angular/core';
import {FormBuilder, Validators, FormGroup} from "@angular/forms";
import {Router, ActivatedRoute} from "@angular/router";
import {Subscription} from "rxjs/Rx";

import {CustomersService} from "../../../services/customers.service";
import { ValidationService } from 'app/directives';
import {GetValidimageTypes, GetApiurl} from "../../../parameters";
import { CustomerItems } from '../../../landing-page/partner/partner-registration';


@Component({
    selector: 'app-customers-edit',
    templateUrl: './customers-edit.component.html',
    styleUrls: ['./customers-edit.component.scss']
})
export class CustomersEditComponent implements OnInit {
  private editCustomerForm: FormGroup;
  private logoError: string;
  private imageFileName: string;
  private imageFile: any;
  private subscription: Subscription;
  private showcustomerstatus: any;
  private customerId: number;
  private customerdetail: any;
  private contactId: any;
  private contactdetail: any;
  private optinalcontactdetail: any;
  private optionalId: any;
  private logo: any;
  private companyErrorMsg: any;
  private panNumberErrorMsg: any;
  private routerurl: any;
  private routerevents: any;
  customerItems: any = CustomerItems();
  private customerValue: any = [];
  public deliverySequenceItems;
  public segmentItems = ['SMB', 'Non-SMB']

  constructor(private fb: FormBuilder, private router: Router, private service: CustomersService, private activatedRoute: ActivatedRoute) {
    this.routerurl = router['url'];
    console.log(this.routerurl)
    let id
    this.subscription = this.activatedRoute.params.subscribe(
      (param: any) => {
         id = param['id'];
        this.getCustomerById(id);
        this.customerId = id
        this.getDeliverySequence(id)

      });

  }

  ngOnInit() {
  }

  private getCustomerById(id) {
    this.service.getCustomersList(id)
      .then(data => {
        console.log(data);
        localStorage.setItem('customer_name', data.customerdetails[0]['company_name']);
        let customerInfo = data.customerdetails[0];
        let primaryContact = data.customercontacts[0];
        let secondaryContact = data.customercontacts[1];
        this.customerdetail = customerInfo['id'];
        this.contactdetail = primaryContact['id'];
        this.optinalcontactdetail = secondaryContact['id'];
        if (customerInfo['logo'] != '') {
          this.logo = GetApiurl(`uploads/` + customerInfo['logo'])
        }
        else {
          this.logo = './../../../assets/img/noimage.jpg'
        }
        let customer_vertical_array: Array<any>;
        let customerVertical = 0;
        if (customerInfo['customer_vertical']) {
          customerVertical = parseInt(customerInfo['customer_vertical']) - 1;
        }
        customer_vertical_array = [this.customerItems[customerVertical]];

        this.editCustomerForm = this.fb.group({
          'company_name': [customerInfo['company_name'], [Validators.required]],
          'address': [customerInfo['address'], [Validators.required]],
          'postcode': [customerInfo['Pincode'], [Validators.required]],
          'city': [customerInfo['city'], [Validators.required]],
          'state': [customerInfo['state'], [Validators.required]],
          'country': [customerInfo['country'], [Validators.required]],
          'pan_number': [customerInfo['pan_number']],
          'contact_name': [primaryContact['name'], [Validators.required]],
          'position': [primaryContact['position']],
          'email': [primaryContact['email'], [Validators.required, ValidationService.emailValidator]],
          'mobile': [primaryContact['mobile'], [Validators.required, ValidationService.phoneValidator]],
          'optional_contact_name': [secondaryContact['name']],
          'optional_contact_position': [secondaryContact['position']],
          'optional_contact_email': [secondaryContact['email']],
          'optional_contact_mobile': [secondaryContact['mobile']],
          'customer_vertical': [customer_vertical_array, [Validators.required]],
          'delivery':[customerInfo['delivery_sequence'],[Validators.required]],
          'segment': ['', [Validators.required]]

        });
        this.CheckValue(customerInfo)
        this.showcustomerstatus = true;

      })

  }

  getDeliverySequence(id) {
    let customer=id
    this.service.deliverySequence(customer)
      .then(data => {
        console.log(data)
        if (data.length != 0) {
          this.deliverySequenceItems = data;
        }
        else {
          this.deliverySequenceItems = [{'dDSEQ': '000'}]
        }
      })

  }

  private editCustomerDetails(formvalues: any) {
    formvalues.customerId = this.customerdetail;
    formvalues.contactId = this.contactdetail;
    formvalues.optionalId = this.optinalcontactdetail;
    this.service.updateCustomer(formvalues, this.imageFile)
      .then(data => {
        this.router.navigate(['/app/customers/list']);
      })
  }

  //updating checking companyname validation starts here
  private checkCompanyNameExist(event) {
    event.preventDefault();
    let id = this.customerId;
    this.service.checkcompanyName(event.target.value, id)
      .then(data => {
        if (data != '') {
          this.companyErrorMsg = 'Company name already exists.'
        }
        else {
          this.companyErrorMsg = null
        }
      });
  }

  //updating checking pancard no validation starts here
  private checkPanNumberExist(event) {
    let id = this.customerId;
    this.service.checkPanNumber(event.target.value, id)
      .then(data => {
        if (data != '') {
          this.panNumberErrorMsg = 'PAN number already exists.'
        }
        else {
          this.panNumberErrorMsg = null
        }
      });
  }

  private previewFile(aggrementFile) {
    var reader = new FileReader();
    let previewElement = jQuery('#vendorlogoid');
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
      this.logoError = 'Please upload an image file.'
      this.imageFileName = null
      jQuery('#vendorlogoid').attr('src', './../../../assets/img/noimage.jpg');
    } else if (imageFileSize > validImageTypesandSize.validSize) {
      this.logoError = 'Please upload a file less than 1MB';
      this.imageFileName = null
      jQuery('#vendorlogoid').attr('src', './../../../assets/img/noimage.jpg');
    } else {
      this.imageFile = imageFile;
      this.logoError = null;
      this.imageFileName = imageFileName;
      this.previewFile(imageFile);

    }

  }

  public backToList() {
    this.router.navigate(['/app/customers/list']);
  }

  public cancel() {
    this.router.navigate(['/app/customers/list']);
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

  public CheckValue(customerInfo) {
    if(customerInfo['segment']=='SMB') {
      this.editCustomerForm.controls['segment'].setValue([{'id': 'SMB', 'text': 'SMB'}])
    }
    else{
      this.editCustomerForm.controls['segment'].setValue([{'id': 'Non-SMB', 'text': 'Non-SMB'}])
    }

  }
}
