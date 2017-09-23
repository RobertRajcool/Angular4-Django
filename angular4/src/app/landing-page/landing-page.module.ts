import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { LandingPageRouting } from './landing-page.routing';
import { LandingPageComponent } from './landing-page.component';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { HomeComponent } from './home/home.component';
import { PartnerComponent } from './partner/partner.component';
import { AuthComponent } from './auth/auth.component';
import { LoginComponent } from './auth/login/login.component';
import { PasswordResetComponent } from './auth/password-reset/password-reset.component';
import { PasswordResetConfirmComponent } from './auth/password-reset-confirm/password-reset-confirm.component';

import { PartnerService } from './partner/partner.service';
import { BootstrapWizardModule } from '../components/wizard/wizard.module'; // wizard module
import { SharedModule } from 'app/shared';
import { UnifyTemplateModule } from '../../assets/Unify-template/unify-template.module';
import { ResponsiveSlidesModule } from '../../assets/Login-001/responsive-slides.module';

// For fils upload
import 'jasny-bootstrap/docs/assets/js/vendor/holder.js';
import 'jasny-bootstrap/js/fileinput.js';
import 'jasny-bootstrap/js/inputmask.js';
// For frontend validation
import 'parsleyjs';
import { MsCreateCustomerComponent } from './ms-create-customer/ms-create-customer.component';


@NgModule({ 
  imports: [
    CommonModule,
    LandingPageRouting,
    FormsModule,
    ReactiveFormsModule,
    BootstrapWizardModule,
    SharedModule,
    // UnifyTemplateModule,
    ResponsiveSlidesModule
  ],
  declarations: [
    LoginComponent,
    LandingPageComponent,
    HomeComponent,
    PartnerComponent,
    AuthComponent,
    PasswordResetComponent,
    PasswordResetComponent,
    PasswordResetConfirmComponent,
    MsCreateCustomerComponent,
    ],
    providers: [
      PartnerService
    ]
})
export class LandingPageModule { }
