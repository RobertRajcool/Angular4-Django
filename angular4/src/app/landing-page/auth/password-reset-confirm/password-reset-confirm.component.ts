import { Component, OnInit, OnDestroy, ViewEncapsulation } from '@angular/core';
import { Router, ActivatedRoute } from '@angular/router';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { ValidationService } from 'app/directives';
import { AuthService } from 'app/services/auth/auth.service';

@Component({
    selector: 'app-password-reset-confirm',
    templateUrl: './password-reset-confirm.component.html',
    styleUrls: [
        '../../../../assets/Unify-template/assets/css/style.css',
        '../../../../assets/Unify-template/assets/css/page_log_reg_v4.css',
        '../../../../assets/Unify-template/assets/plugins/line-icons/line-icons.css',
    ]
})
export class PasswordResetConfirmComponent implements OnInit {
    subscriptions: any = {};
    token: string;
    passwordResetForm: FormGroup;
    process: string;
    verificationError: string;
    resetError: string;

    constructor(
        private router: Router,
        private route: ActivatedRoute,
        private fb: FormBuilder,
        private authService: AuthService
    ) {
        this.passwordResetForm = this.fb.group({
            'passwords': this.fb.group({
                'password': ['', [Validators.required, ValidationService.passwordValidator]],
                'confirm_password': ['', [Validators.required, ValidationService.passwordValidator]]
            }, { validator: ValidationService.equalValidator })
        });
    }

    ngOnInit() {
        // Route query params subscription
        this.route.queryParams.subscribe(params => {
            if (Object.keys(params).indexOf('tk') < 0) this.router.navigate(['error/not-found']);
            else {
                this.verifToken(params['tk']);
            }
        });
    }

    // Verifying password reset token
    verifToken(token: string) {
        this.process = 'verifying';

        this.authService
            .verifyPasswordResetToken(token)
            .subscribe(
            Result => {
                this.token = Result;
                this.process = 'verification_success';
            },
            Error => {
                this.process = 'verification_failed';

                if (Error['status_code'] == 500) {
                    this.verificationError = Error['detail'];
                }
                else if (Object.keys(Error).indexOf('non_field_errors') >= 0) {
                    this.verificationError = Error['non_field_errors'].join(', ');
                }

            }
            )
    }

    // Resetting password
    resetPassword() {
        if (this.passwordResetForm.valid) {
            this.process = 'reset_processing';

            this.authService
                .resetPassword(this.token, this.passwordResetForm.value['passwords']['password'])
                .subscribe(
                Result => {
                    this.token = null;
                    this.process = 'reset_success';
                },
                Error => {
                    this.resetError = Error['detail'];
                    this.process = null;
                    this.passwordResetForm.reset();
                });
        }
    }

    // Unsubscribe subscriptions on component destroy
    ngOnDestroy() {
        for (let subscriptionName in this.subscriptions) {
            this.subscriptions[subscriptionName].unsubscribe();
        }
    }
}
