import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from "@angular/forms";
import { Router, ActivatedRoute } from "@angular/router";
import { CustomersService } from 'app/services/customers.service';

@Component({
    selector: 'app-ms-create-customer',
    templateUrl: './ms-create-customer.component.html',
    styleUrls: ['./ms-create-customer.component.scss']
})
export class MsCreateCustomerComponent implements OnInit {
    saving: boolean = false;
    private addCustomerForm: FormGroup;
    subscription: any;
    token: string;
    domain_name_to_display: string;
    valid_token: boolean = true;
    invalid_domain: boolean = false;
    success: boolean = false;

    constructor(private fb: FormBuilder, private router: Router, private route: ActivatedRoute, private cs:CustomersService) {
        this.route
            .queryParams
            .subscribe(params => {
                this.token = params['token'];
                this.authenticateToken();
            });
    }

    ngOnInit() {
        let domainRegex = new RegExp("^[a-zA-Z0-9][a-zA-Z0-9-]{1,61}[a-zA-Z0-9]+$");
        this.addCustomerForm = this.fb.group({
            'domain_name': ['', [Validators.required, Validators.pattern(domainRegex)]]
        });
    }

    authenticateToken() {
        this.cs.authenticateToken(this.token).then(data=>this.valid_token=data);
    }

    createCustomer() {
        this.invalid_domain = false;
        this.saving = true;
        this.domain_name_to_display = this.addCustomerForm.controls['domain_name'].value + '.onmicrosoft.com';
        let customerData = {
            'domain_name': this.addCustomerForm.controls['domain_name'].value,
            'token': this.token
        };

        this.cs.createMSCustomer(customerData).then(data=>{
            if(data == 'domain_exist') {
                this.invalid_domain = true;
            } else if(data == 'Failed') {
                alert('Failed to create customer, Please try again')
            } else if(data == 'Success') {
                this.success = true;
            }
            this.saving = false;
        });
    }

}
