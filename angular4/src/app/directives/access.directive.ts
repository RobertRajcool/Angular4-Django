import { Directive, TemplateRef, ViewContainerRef, Input, OnInit, OnDestroy } from '@angular/core';
import { GlobalsService } from 'app/services';
import { Subscription } from 'rxjs/Subscription';
import { User } from 'app/classes';

@Directive({
    selector: '[access]'
})
export class AccessDirective {
    user_permissions: Array<string> = [];
    userDetails: User = new User(null, null, null, null, null, null);
    allowedRoles: Array<string> = [];
    permitted: boolean = false;
    isUserTypeValid: boolean = true;
    subscriptions: Object = {};

    constructor(
        private template_ref: TemplateRef<any>,
        private view_container_ref: ViewContainerRef,
        private globals: GlobalsService
    ) {
        // Subscribe globals property
        // User permissions subscription
        this.subscriptions['userPermissionsSubscription'] = this.globals.userPermissions$.subscribe(permissions => {
            if (permissions instanceof Array) this.user_permissions = permissions;
        });

        // User details subscription
        this.subscriptions['userDetailsSubscription'] = this.globals.user$.subscribe(details => {
            if (details) this.userDetails = details;
        });
    }

    // Add or Remove element based on roles
    @Input() set access(roles: Array<string>) {
        this.allowedRoles = roles;
        this.permitted = this.intersect(this.user_permissions, roles).length == roles.length;

        this.bindTemplate();
    }

    // Add or Remove element based on user type
    @Input('accessTypes')
    set types(allowedTypes: Array<string>) {


        if (!allowedTypes) this.isUserTypeValid = true;
        else {
            if (this.userDetails['is_superuser']) this.isUserTypeValid = allowedTypes.indexOf('R') >= 0;
            else this.isUserTypeValid = allowedTypes.indexOf(this.userDetails.user_type) >= 0;
        }

        this.bindTemplate();
    }

    // Add or Remove element based on roles by checking is any one enabled
    @Input('accessAnyOne')
    set anyOne(isTrue: boolean) {
        if (this.allowedRoles.length > 0) {
            if (isTrue) this.permitted = this.intersect(this.user_permissions, this.allowedRoles).length > 0;
            else this.permitted = this.intersect(this.user_permissions, this.allowedRoles).length == this.allowedRoles.length;
        }

        this.bindTemplate();
    }

    // Add or Remove element
    bindTemplate() {
        this.view_container_ref.clear();

        if (this.permitted && this.isUserTypeValid) this.view_container_ref.createEmbeddedView(this.template_ref);

    }

    // Finding common elements from two arrays
    intersect(a, b) {
        var t;
        if (b.length > a.length) t = b, b = a, a = t; // indexOf to loop over shorter
        return a.filter(e => b.indexOf(e) > -1).filter((e, i, c) => c.indexOf(e) === i);// extra step to remove duplicates
    }

    // unsubscribing subacriptions 
    ngOnDestroy() {
        Object.keys(this.subscriptions).forEach(subscriptionName => {
            this.subscriptions[subscriptionName].unsubscribe();
        })
    }
}
