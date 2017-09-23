import { NgModule } from '@angular/core';
import { SharedModule } from '../../../shared/shared.module';

// Declarations
import { CustomersComponent } from './customers.component';
import { CustomersListComponent } from './customers-list/customers-list.component';

// Routing
import { CustomersRouting } from './customers.routing';

@NgModule({
    imports: [
        SharedModule,
        CustomersRouting
    ],
    declarations: [
        CustomersComponent,
        CustomersListComponent
    ],
    providers: [
      
    ]
})

export class CustomersModule {}