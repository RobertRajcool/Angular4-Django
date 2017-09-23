import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { CustomersListComponent } from './customers-list/customers-list.component';
import { CustomersRouting } from './customers.routing';
import { CustomersComponent } from './customers/customers.component'
import { SharedModule } from "app/shared";
import { PaginationModule } from 'ng2-bootstrap';
import { CustomersService } from 'app/services';
//import { CustomersEditComponent } from './customers-edit/customers-edit.component'
import { Ng2TableModule } from "ng2-table/ng2-table";
//import {CustomersViewComponent} from "./customers-view/customers-view.component";
import { ComponentSharedModule } from '../../shared/component-shared.module';


@NgModule({
    imports: [
        CommonModule,
        CustomersRouting,
        SharedModule,
        PaginationModule.forRoot(),
        Ng2TableModule,
        ComponentSharedModule
    ],
    declarations: [CustomersListComponent, CustomersComponent],
    providers: [CustomersService]
})
export class CustomersModule { }
