import { NgModule, TemplateRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { RouterModule } from '@angular/router';
import { DirectivesModule } from 'app/directives/directives.module';
import { PipesModule } from 'app/pipes';
import { NfActionsComponent } from 'app/portal/notifications/nf-actions/nf-actions.component';
import { Ng2TableComponent } from 'app/directives/ng2-table/ng2-table.component';
import { Ng2TableModule } from 'ng2-table/ng2-table';
import { PaginationModule } from 'ng2-bootstrap';
import { SelectModule } from 'ng2-select';
import { NKDatetimeModule } from 'ng2-datetime/ng2-datetime';//datepicker module
//import { OfferPreviewComponent } from 'app/portal/offers/offer-preview/offerpreview.component';
import { RedTableComponent } from 'app/directives/red-table/red-table.component';
import { RedPdfReportComponent } from 'app/directives/red-pdf-report/red-pdf-report.component';
import { RedExcelReportComponent } from 'app/directives/red-excel-report/red-excel-report.component';
import { PartnerDetailsComponent } from './../portal/partner/partner-view/partner-details/partner-details.component';
//import {SoftlayerVmExtrainputsComponent} from 'app/directives/softlayer-vm-extrainputs/softlayer-vm-extrainputs.component';
//import { MarketPlaceScroller } from 'app/directives/mp-scroller/mp-scroller.component';
//import { MpCloudtemplateScrollerComponent } from 'app/directives/mp-cloudtemplate-scroller/mp-cloudtemplate-scroller.component';
//import { PartnerActivateComponent } from '../portal/partner/partner-activate/partner-activate.component';
//import { DiskCreationComponent } from '../portal/market-place/mp-advanced-mode/disk-creation/disk-creation.component';
import { ChangePasswordComponent } from '../portal/change-password/change-password.component';
import { EqualValidator } from '../portal/change-password/change-password.component';
import { PartnerActivateComponent } from '../portal/partner/partner-activate/partner-activate.component'
import { AlertModule, TooltipModule,
    ButtonsModule, BsDropdownModule } from 'ngx-bootstrap';
import { Ng2BreadcrumbModule, BreadcrumbService } from 'ng2-breadcrumb/ng2-breadcrumb';
    
@NgModule({
    imports: [
        // Angular modules
        CommonModule,
        FormsModule,
        ReactiveFormsModule,
        RouterModule,

        // Custom modules
        PipesModule,
        DirectivesModule,

        // Third party modules
        Ng2TableModule,
        PaginationModule.forRoot(),
        TooltipModule.forRoot(),
        AlertModule.forRoot(),
        SelectModule,
        NKDatetimeModule,
       // Ng2BreadcrumbModule.forRoot()

    ],
    declarations: [
        // Custom directives
        Ng2TableComponent,

        // Custom components
        NfActionsComponent,
        RedTableComponent,
        RedPdfReportComponent,
        RedExcelReportComponent,
        //partner details component
        PartnerDetailsComponent,
        ChangePasswordComponent,
        EqualValidator,
        PartnerActivateComponent

        // Third party

    ],
    providers: [

    ],
    exports: [
        // Angular modules
        CommonModule,
        FormsModule,
        ReactiveFormsModule,

        // Custom modules
        PipesModule,
        DirectivesModule,

        // Custom directives
        Ng2TableComponent,
        RedTableComponent,
        RedPdfReportComponent,
        RedExcelReportComponent,

        // Custom components
        NfActionsComponent,

        // Third party
        Ng2TableModule,
        PaginationModule,
        SelectModule,
        TooltipModule,
        AlertModule,

        //Date pikcer module
         NKDatetimeModule,
        ChangePasswordComponent,
        EqualValidator,
        PartnerActivateComponent,
        DirectivesModule
        //Ng2BreadcrumbModule
    ]
})
export class SharedModule { }
