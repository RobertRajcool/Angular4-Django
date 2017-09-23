import { Component, OnInit, ViewEncapsulation } from '@angular/core';
import { Router } from '@angular/router';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { GlobalsService,  } from 'app/services';
import { AuthService } from 'app/services/auth/auth.service'
import { Angulartics2 } from 'angulartics2';

@Component({
    selector: 'app-login',
    encapsulation: ViewEncapsulation.Emulated,
    templateUrl: './login.component.html',
    styleUrls: [
        '../../../../assets/Unify-template/assets/css/style.css',
        '../../../../assets/Unify-template/assets/css/page_log_reg_v4.css',
        '../../../../assets/Unify-template/assets/plugins/line-icons/line-icons.css',
    ]
})

export class LoginComponent implements OnInit {
    loginForm: FormGroup;
    loginError: string;
    process: string;

    constructor(
        private fb: FormBuilder,
        private authService: AuthService,
        private router: Router,
        private globals: GlobalsService,
        private angulartics2: Angulartics2) {

        // Building login form
        this.loginForm = this.fb.group({
            'username': ['', [Validators.required]],
            'password': ['', [Validators.required]]
        });
    }

    ngOnInit() { }

    // Login action
    login() {
        this.process = 'checking';
        let formValue = this.loginForm.value;

        this.authService.login(formValue.username, formValue.password)
            .subscribe(
            response => {
                this.loginError = null;
                
                // Recording for google analytics
                this.angulartics2.eventTrack.next({
                    action: 'Login',
                    properties: {
                        category: 'Authentication'
                    }
                });
                this.authService.redirectToHome();
            },
            error => {
                this.process = null;
                this.handleError(error);
            }
            );
    }

    // Handeling errors
    handleError(error: any) {
        console.log(error);
        if (new RegExp('Unable to login').test(error)) {
            this.loginError = 'Invalid credentials';
        }
        else {
            this.loginError = error;
        }
    }
}
