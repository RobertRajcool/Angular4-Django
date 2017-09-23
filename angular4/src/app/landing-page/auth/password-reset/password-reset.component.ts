import { Component, OnInit, OnDestroy, ViewEncapsulation } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { ValidationService } from 'app/directives';
import { AuthService } from 'app/services/auth/auth.service';

@Component({
    selector: 'app-password-reset',
    encapsulation: ViewEncapsulation.Emulated,
    templateUrl: './password-reset.component.html',
    styleUrls: [
        '../../../../assets/Unify-template/assets/css/style.css',
        '../../../../assets/Unify-template/assets/css/page_log_reg_v4.css',
        '../../../../assets/Unify-template/assets/plugins/line-icons/line-icons.css',
    ]
})
export class PasswordResetComponent implements OnInit {
    process: string;
    verificationForm: FormGroup;
    verificationError: {
        target: string;
        msg: string;
    };
    verificationSuccess: any;

    constructor(
        private fb: FormBuilder,
        private authService: AuthService
    ) { }

    ngOnInit() {

        // Building details verification form 
        this.verificationForm = this.fb.group({
            'username': ['', [Validators.required]],
            'email': ['', [Validators.required, ValidationService.emailValidator]]
        });
    }

    generateResetLink() {
        this.process = 'checking';
        this.verificationError = null;

        if (this.verificationForm.valid) {
            let details = this.verificationForm.value;
            this.authService
                .generatePasswordResetLink(details['username'], details['email'])
                .subscribe(
                Result => {
                    this.process = "link_emailed";
                    this.verificationSuccess = Result;
                },
                Error => {
                    if (Error['status_code'] == 500) {
                        if (new RegExp("Username", "g").test(Error['detail'])) {
                            this.verificationError = {
                                target: 'username',
                                msg: Error['detail']
                            }
                        }
                        else if (new RegExp("Email", "g").test(Error['detail'])) {
                            this.verificationError = {
                                target: 'email',
                                msg: Error['detail']
                            }
                        }
                        else {
                            this.verificationError = {
                                target: 'undefined',
                                msg: Error['detail']
                            }
                        }
                    }
                    this.process = null;
                }
                )
        }
    }

}
