import { Component, OnInit,Input } from '@angular/core';
import {ResponseContentType, Http, Headers} from "@angular/http";
import {RedConstants} from '../../classes/constants'
declare var saveAs:any;
@Component({
    selector: 'app-red-pdf-report',
    templateUrl: './red-pdf-report.component.html',
    styleUrls: ['./red-pdf-report.component.scss']
})
export class RedPdfReportComponent implements OnInit {
    @Input() backend_fetchUrl_pdf: string;
    @Input() commonFilter_Pdf: any;
    @Input() screenName:string
    constructor(private http:Http) { }

    ngOnInit()
    {
    }
    public downloadPDF_File() {
        this.downloadPDF().subscribe(
            (res) => {
               /*
               if we want new window
                var fileURL = URL.createObjectURL(res);
                window.open(fileURL);*/
               saveAs(res,this.screenName+'.pdf')
            }
        );
    }
    private constructURL(): string {
        let url = this.backend_fetchUrl_pdf + '?reportstatus=' + RedConstants.PDFREPORT_STATUS;
        if(this.commonFilter_Pdf.length) {
            this.commonFilter_Pdf.forEach((column:any) => {
                let encodevalue=encodeURIComponent(column.value)
                url += '&' + column.name + '=' + encodevalue;
            });
        }
        return url;
    }
    public downloadPDF(): any {
        let url=this.constructURL()
        let headers = new Headers();
        headers.append('Authorization', 'JWT ' + localStorage.getItem('id_token'));
        return this.http.get(url,{  headers: headers,responseType: ResponseContentType.Blob }).map(
            (res) => {
                return new Blob([res.blob()], { type: 'application/pdf' })
            })
    }

}
