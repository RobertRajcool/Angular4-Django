import { Component, EventEmitter, OnInit, ElementRef, Output, OnDestroy } from '@angular/core';
import { Router } from '@angular/router';
import { FormBuilder, FormGroup, FormControl, Validators } from '@angular/forms';
import { AppConfig,  GlobalsService } from 'app/services';
import { AuthService } from 'app/services/auth/auth.service';
import { PartnerService } from '../partner/partner.service';
import { Subscription } from 'rxjs/Subscription';
import { User } from 'app/classes';
import { GetApiurl } from '../../parameters';

declare var jQuery: any;

@Component({
    selector: '[navbar]',
    templateUrl: './navbar.template.html'
})
export class Navbar implements OnInit {
    @Output() toggleSidebarEvent: EventEmitter<any> = new EventEmitter();
    @Output() toggleCartEvent: EventEmitter<any> = new EventEmitter();
    $el: any;
    config: any;
    router: Router;
    subscriptions: Object = {};
    unread_notifications: number = 0;
    user_details: User;
    partner: any;
    recipientOptions: Array<{
        id: string;
        text: string;
    }> = [];
    remoteConfig: any = {
        url: '',
        searchField: 'username',
        debounceTime: 500,
        authentication: true,
        tokenId: 'id_token',
        tokenStorage: 'localStorage',
        idField: 'id',
        textField: 'username'
    };
    searchForm: FormGroup;
    cartCount: number = 0;

    constructor(
        el: ElementRef,
        config: AppConfig,
        router: Router,
        private authService: AuthService,
        private gsService: GlobalsService,
        private fb: FormBuilder,
        private partnerService: PartnerService
    ) {
        this.$el = jQuery(el.nativeElement);
        this.config = config.getConfig();
        this.router = router;

        // Subscribing globals services
        this.subscriptions['userSubscription'] = this.gsService.user$.subscribe(user => {
             if (user) this.user_details = user;
            else this.user_details = new User(null, null, null, null, null, null);
         });
        this.subscriptions['notificationSubcription'] = this.gsService.unread_notifications$.subscribe(count => this.unread_notifications = count);

        // Build form
        this.searchForm = this.fb.group({
            'option': ['', Validators.required]
        });

        // Use search url based on user type
        if (this.user_details.user_type != "P" && this.user_details.user_type != "C") {
            this.remoteConfig.url = GetApiurl('partner_details/search-partner/');
            this.remoteConfig.searchField = 'company_name';
            this.remoteConfig.textField = 'company_name';
        } else if (this.user_details.user_type == "P") {
            this.remoteConfig.url = GetApiurl('customers/' + this.user_details.id + '/search/');
            this.remoteConfig.searchField = 'company_name';
            this.remoteConfig.textField = 'company_name';
            this.partnerService.getCurrentPartnerDetail().subscribe(partner => {
                this.partner = partner;
            });
        }
    }

    toggleSidebar(state): void {
        this.toggleSidebarEvent.emit(state);
    }

    toggleCart(): void {
        this.toggleCartEvent.emit(null);
    }

    onDashboardSearch(f): void {
        // this.router.navigate(['/app', 'extra', 'search'], { queryParams: { search: f.value.search } });
    }

    public selected(value: any): void {
        if (value) {
            let id: number = value['id'];
            if (this.user_details.user_type != "P" && this.user_details.user_type != "C") {
                this.router.navigateByUrl("/app/partner/" + id + "/details");
            } else {
                this.router.navigateByUrl("/app/customers/" + id + "/details");
            }
        }
    }

    ngOnInit(): void {
        // Cart items subscription
        /* this.subscriptions['cartItemsSubscription'] = this.cartService.cartItems$.subscribe(Items => {
            this.cartCount = Items.length;
        }); */


        setTimeout(() => {
            let $chatNotification = jQuery('#chat-notification');
            $chatNotification.removeClass('hide').addClass('animated fadeIn')
                .one('webkitAnimationEnd mozAnimationEnd MSAnimationEnd oanimationend animationend', () => {
                    $chatNotification.removeClass('animated fadeIn');
                    setTimeout(() => {
                        $chatNotification.addClass('animated fadeOut')
                            .one('webkitAnimationEnd mozAnimationEnd MSAnimationEnd' +
                            ' oanimationend animationend', () => {
                                $chatNotification.addClass('hide');
                            });
                    }, 8000);
                });
            $chatNotification.siblings('#toggle-chat')
                .append('<i class="chat-notification-sing animated bounceIn"></i>');
        }, 4000);

        this.$el.find('.input-group-addon + .form-control').on('blur focus', function (e): void {
            jQuery(this).parents('.input-group')
            [e.type === 'focus' ? 'addClass' : 'removeClass']('focus');
        });
    }

    Logout() {
        this.authService.logout();
    }

    openHelpModal(){
        jQuery('#exr-update-rate-mod').modal('show');
    }

    // Unsubscribe subscriptions on component destroy
    ngOnDestroy() {
        for (let subscriptionName in this.subscriptions) {
            this.subscriptions[subscriptionName].unsubscribe();
        }
    }

}
