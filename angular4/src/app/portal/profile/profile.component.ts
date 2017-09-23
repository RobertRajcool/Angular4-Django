import { Component, OnInit, OnDestroy } from '@angular/core';
import { GlobalsService } from 'app/services';
import { Subscription } from 'rxjs/Subscription';
import { User } from 'app/classes';

@Component({
    selector: 'app-profile',
    templateUrl: './profile.component.html',
    styleUrls: ['./profile.component.scss']
})
export class ProfileComponent implements OnInit {
    subscriptions: Object = {};
    user_details: User;

    constructor(
        private gsService: GlobalsService
    ) { }

    ngOnInit() {

        // Subscribing globals services
        this.subscriptions['userSubscription'] = this.gsService.user$.subscribe(user => this.user_details = user);
    }

    // Unsubscribe subscriptions on component destroy
    ngOnDestroy() {
        for (let subscriptionName in this.subscriptions) {
            this.subscriptions[subscriptionName].unsubscribe();
        }
    }

}
