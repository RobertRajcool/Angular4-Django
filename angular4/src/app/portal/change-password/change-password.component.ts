import { Component, OnInit } from '@angular/core';
import { FormGroup, Validators, FormBuilder } from "@angular/forms";
import { ValidationService } from 'app/directives';
import { ChangePasswordService } from "./change-password.service";
import { GlobalsService } from "app/services";
import { Router } from "@angular/router";
@Component({
  selector: 'app-change-password',
  templateUrl: './change-password.component.html',
  styleUrls: ['./change-password.component.scss']
})
export class ChangePasswordComponent implements OnInit {
    private change_passwordForm: FormGroup
    private process: boolean

    constructor(private fb: FormBuilder,
        private password_service: ChangePasswordService,
        private gs: GlobalsService,
        private router: Router) { }

    ngOnInit() {
        this.change_passwordForm = this.fb.group({
            'old_password': ['', [Validators.required]],
            'password': ['', [Validators.required, ValidationService.passwordValidator]],
            'confirm_password': ['', [Validators.required, ValidationService.passwordValidator]]
        })
    }
    private changePassword(values) {
        this.process = true
        this.password_service.changePassword(values).subscribe(data => {
            if (data.hasOwnProperty('msg')) {
                this.change_passwordForm.controls['old_password'].setErrors({ 'errors': data['msg'] })
            }
            else {
                this.gs.setToastMessage(data['suc_msg'], 3000)
                if (this.router.url.indexOf('isv') != -1) {

                    this.router.navigate(['/isv/dashboard']);
                }
                else {

                    this.router.navigate(['/app/dashboard']);
                }
            }
            this.process = null
        },
            error => {
                this.process = null
                console.log(error)
            })
    }

}

// equal-validator.directive.ts

import { Directive, forwardRef, Attribute } from '@angular/core';
import { Validator, AbstractControl, NG_VALIDATORS } from '@angular/forms';

@Directive({
    selector: '[validateEqual][formControlName],[validateEqual][formControl],[validateEqual][ngModel]',
    providers: [
        { provide: NG_VALIDATORS, useExisting: forwardRef(() => EqualValidator), multi: true }
    ]
})
export class EqualValidator implements Validator {
    constructor( @Attribute('validateEqual') public validateEqual: string,
        @Attribute('reverse') public reverse: string) {
    }

    private get isReverse() {
        if (!this.reverse) return false;
        return this.reverse === 'true' ? true : false;
    }

    validate(c: AbstractControl): { [key: string]: any } {
        // self value
        let v = c.value;

        // control vlaue
        let e = c.root.get(this.validateEqual);

        // value not equal
        if (e && v !== e.value && !this.isReverse) {
            return {
                validateEqual: 'Password mismatch'
            }
        }

        // value equal and reverse
        if (e && v === e.value && this.isReverse) {
            delete e.errors['validateEqual'];
            if (!Object.keys(e.errors).length) e.setErrors(null);
        }

        // value not equal and reverse
        if (e && v !== e.value && this.isReverse) {
            e.setErrors({ validateEqual: 'Password mismatch' });
        }

        return null;
    }
}