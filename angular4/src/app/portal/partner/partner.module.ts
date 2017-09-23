import { NgModule } from '@angular/core';
import { SharedModule } from '../../shared/shared.module';
import { ComponentSharedModule } from '../../shared/component-shared.module';

// Declarations
import { PartnerComponent } from './partner.component';
import { PartnerListComponent } from './partner-list/partner-list.component';


// Routing
import { PartnerRouting } from './partner.routing';

// Services
import { PartnerService } from './partner.service';
import { InactivePartnerService } from './../inactive-partner/inactive-partner.service';

// Directives
import { PaginationModule } from 'ng2-bootstrap';
import { Select2Module } from 'ng2-select2';
import { ModalModule } from 'ng2-modal';
import { TabsModule, AccordionModule } from 'ng2-bootstrap';
import { Ng2TableModule } from 'ng2-table/ng2-table';
import { SelectModule } from 'ng2-select';

@NgModule({
    imports: [
        PartnerRouting,
        SharedModule,
        ComponentSharedModule,
        PaginationModule.forRoot(),
        Select2Module,
        ModalModule,
        TabsModule.forRoot(),
        AccordionModule.forRoot(),
        Ng2TableModule,
        SelectModule
    ],
    declarations: [
        PartnerComponent,
        PartnerListComponent
    ],
    providers: [
      PartnerService,
      InactivePartnerService
    ]
})

export class PartnerModule {}
