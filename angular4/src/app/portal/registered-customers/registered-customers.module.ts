import { NgModule } from '@angular/core';
import { SharedModule } from '../../shared/shared.module';
import { ComponentSharedModule } from '../../shared/component-shared.module';

import { InactiveCustomersComponent } from './inactive-customers/inactive-customers.component';
import { ActiveCustomersComponent } from './active-customers/active-customers.component';

// Directives
import { PaginationModule } from 'ng2-bootstrap';
import { Select2Module } from 'ng2-select2';
import { ModalModule } from 'ng2-modal';
import { TabsModule, AccordionModule } from 'ng2-bootstrap';
import { Ng2TableModule } from 'ng2-table/ng2-table';
import { SelectModule } from 'ng2-select';

// Services
import { RegisteredCustomersService } from 'app/services/index';

// Routing
import { RegisteredCustomerRouting } from './registered-customers.routing';

@NgModule({
    imports: [
        SharedModule,
        ComponentSharedModule,
        PaginationModule.forRoot(),
        Select2Module,
        ModalModule,
        TabsModule.forRoot(),
        AccordionModule.forRoot(),
        Ng2TableModule,
        SelectModule,
        RegisteredCustomerRouting
    ],
    declarations: [ 
    InactiveCustomersComponent,
    ActiveCustomersComponent
    ],
    providers: [
      RegisteredCustomersService
    ]
})

export class RegisteredCustomerModule {}