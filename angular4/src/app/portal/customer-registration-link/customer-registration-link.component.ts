import { Component, OnInit } from '@angular/core';
import { Router, ActivatedRoute, Params } from '@angular/router';
import { FormGroup, FormBuilder, Validators } from '@angular/forms';
import { ValidationService } from 'app/directives';
import { PartnerService } from '../partner/partner.service';
import { GlobalsService } from 'app/services';

@Component({
  selector: 'app-customer-registration-link',
  templateUrl: './customer-registration-link.component.html',
  styleUrls: ['./customer-registration-link.component.scss']
})
export class CustomerRegistrationLinkComponent implements OnInit {

  customerRegForm: FormGroup;
  progress: string = undefined;

  constructor(private fb: FormBuilder, private route: Router, private service: PartnerService, private gs: GlobalsService) { }

  ngOnInit() {
    this.buildForm();
  }

  buildForm() {
    this.customerRegForm = this.fb.group({
                'customer': ['', [ Validators.required ]],
                'email': ['', [ Validators.required, ValidationService.emailValidator ]]
            }
        )
  }

  sendLink() {
    this.progress = 'sending';
    this.service.sendLinkService(this.customerRegForm.value).then(res => {
        this.progress = undefined;
        this.buildForm();
        this.gs.setToastMessage('Registration link send successfully!', 5000);
    })
  }

}
