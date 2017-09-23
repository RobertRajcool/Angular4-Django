import { CustomersViewComponent } from "app/portal/customers/customers-view/customers-view.component";
import {CustomersEditComponent} from "app/portal/customers/customers-edit/customers-edit.component";
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { DirectivesModule } from 'app/directives/directives.module';
import { CommonModule } from '@angular/common';
import { NgModule, TemplateRef } from '@angular/core';
import { SharedModule } from 'app/shared';
import { RouterModule } from '@angular/router';
import {AddComponent} from "../portal/customers/add/add.component";
//import {InvoicesListComponent} from '../portal/invoices/invoices-list/invoices-list.component';

import { CustomerCloudAccountsDetailsComponent } from '../portal/customers/customer-cloud-accounts-details/customer-cloud-accounts-details.component';

import { CustomerCloudAccountsService } from 'app/services';

@NgModule({
    imports: [
     SharedModule,
      RouterModule

    ],
    declarations: [
      CustomersEditComponent,
      CustomersViewComponent,
      AddComponent,
      CustomerCloudAccountsDetailsComponent
    ],
    providers: [
      CustomerCloudAccountsService
    ],
    exports: [
      CustomersEditComponent,
      CustomersViewComponent,
      AddComponent,
      CustomerCloudAccountsDetailsComponent

    ]
})
export class ComponentSharedModule { }
