import { NgModule } from '@angular/core';
import { SharedModule } from 'app/shared/shared.module';

// Routing
import { InactivePartnerRouting } from './inactive-partner.routing';

// Services
import { InactivePartnerService } from './inactive-partner.service';

//  Declarartions
import { InactivePartnerComponent } from './inactive-partner.component';
import { InactivePartnerListComponent } from './inactive-partner-list/inactive-partner-list.component';
import { PaginationModule } from 'ng2-bootstrap';

@NgModule({
    imports: [
        SharedModule,
        InactivePartnerRouting,
        PaginationModule.forRoot()
    ],
    declarations: [
        InactivePartnerComponent,
        InactivePartnerListComponent
    ],
    providers: [
        InactivePartnerService
    ]
})
export class InactivePartnerModule { }
