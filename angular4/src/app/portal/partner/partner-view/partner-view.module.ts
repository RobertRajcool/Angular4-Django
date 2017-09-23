import { NgModule } from '@angular/core';
import { SharedModule } from '../../../shared/shared.module';

// Declarations
import { PartnerViewComponent } from './partner-view.component';
import { CustomersListComponent } from './../customers/customers-list/customers-list.component';

// Routing
import { PartnerViewRouting } from './partner-view.routing';

// Directives
import { TabsModule, AccordionModule } from 'ng2-bootstrap';
import { OrdersComponent } from './../orders/orders.component';
import { ComponentSharedModule } from './../../../shared/component-shared.module';
@NgModule({
    imports: [
        SharedModule,
        PartnerViewRouting,
        TabsModule,
        AccordionModule,
        ComponentSharedModule
    ],
    declarations: [
        PartnerViewComponent,
        CustomersListComponent,
        OrdersComponent,
    ],
    providers: []
})

export class PartnerViewModule {}
