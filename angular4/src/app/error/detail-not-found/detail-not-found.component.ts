import { Component, OnInit, ViewEncapsulation } from '@angular/core';
import { Location } from '@angular/common';
import { ActivatedRoute } from '@angular/router';

@Component({
    selector: 'app-detail-not-found',
    templateUrl: './detail-not-found.component.html',
    encapsulation: ViewEncapsulation.None
})
export class DetailNotFoundComponent implements OnInit {
    details: string;

    constructor(private location: Location, private route: ActivatedRoute) { }

    ngOnInit() {
        this.route.data.subscribe(data =>{ 
            if(Object.keys(data).indexOf('details') >= 0) this.details = data['details'];
        });
    }

    goBack() {
        this.location.back();
    }

    searchResult(): void {
        // this.router.navigate(['/app', 'extra', 'search']);
    }

}
