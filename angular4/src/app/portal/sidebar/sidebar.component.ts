import { Component, OnInit, ElementRef, OnDestroy } from '@angular/core';
import { Router, NavigationEnd } from '@angular/router';
import { Location } from '@angular/common';
import { AppConfig, GlobalsService } from 'app/services';
import { Subscription } from 'rxjs/Subscription';
import { UserService } from '../../users/user.service';
import { RedConstants } from 'app/classes/constants'
declare var jQuery: any;
import * as Raven from 'raven-js';
import 'jquery-slimscroll';
@Component({
    selector: '[sidebar]',
    templateUrl: './sidebar.template.html'
})

export class Sidebar implements OnInit {
    $el: any;
    config: any;
    router: Router;
    location: Location;
    gs_subscription: Subscription;
    user_subscription: Subscription;
    unread_notifications: number = 0;
    userData: any;
    url: any;
    userPartnerDetails: any;
    isMicrosoftUser: boolean = false;
    isAWSUser: boolean = false;
    isIBMUser: boolean = false

    constructor(config: AppConfig, el: ElementRef, router: Router, location: Location, private gsService: GlobalsService, private userService: UserService) {
        this.$el = jQuery(el.nativeElement);
        this.config = config.getConfig();
        this.router = router;
        this.location = location;
        this.user_subscription = this.gsService.user$.subscribe(data => {
            if (data) {
                this.userData = data;
                Raven.setUserContext({id: data.id.toString(), username: data.username, email:''});
                if (data['vendor_category']) {
                    data['vendor_category'].forEach((item, index) => {
                        if (item.vendor_name == 'Microsoft' || item.vendor_name == 'AZURE') {
                            this.isMicrosoftUser = true;
                        } else if (item.vendor_name == 'AWS') {
                            this.isAWSUser = true;
                        }
                        else if (item.vendor_name == RedConstants.IBM_VENDOR) {
                            this.isIBMUser = true
                        }
                    });
                }
                if(this.userData){
                    this.userService.getUserPartnerDetails(this.userData.id).then(data => {
                        this.userPartnerDetails = data;
                        this.url = "/app/partner-profile/" + this.userPartnerDetails;
                        
                    });
                }   

            }
        });
             
        // Subscribe globals services
        this.gs_subscription = this.gsService.unread_notifications$.subscribe(count => this.unread_notifications = count);
    }

    initSidebarScroll(): void {
        let $sidebarContent = this.$el.find('.js-sidebar-content');
        if (this.$el.find('.slimScrollDiv').length !== 0) {
            $sidebarContent.slimscroll({
                destroy: true
            });
        }
        $sidebarContent.slimscroll({
            height: window.innerHeight,
            size: '4px'
        });
    }

    changeActiveNavigationItem(location): void {
        let path: string = location.path().split('?')[0];
        let pathAsArray = path.split('/');
        let count = pathAsArray.length - 1;
        for( let index = count; index > 1; index --) {
            let pathToCheck = pathAsArray.join('/');
            let $newActiveLink = this.$el.find('a[href="' + pathToCheck + '"]');
            if($newActiveLink.length == 1 || pathToCheck.indexOf('dashboard') != -1) {
                this.$el.find('.sidebar-nav .active').removeClass('active');
                // collapse .collapse only if new and old active links belong to different .collapse
                if (!$newActiveLink.is('.active > .collapse > li > a')) {
                    this.$el.find('.active .active').closest('.collapse').collapse('hide');
                }
                $newActiveLink.closest('li').addClass('active')
                    .parents('li').addClass('active');

                // uncollapse parent
                $newActiveLink.closest('.collapse').addClass('in').css('height', '')
                    .siblings('a[data-toggle=collapse]').removeClass('collapsed');
                break;
            }
            pathAsArray.pop()
        }
    }

    ngAfterViewInit(): void {
        this.changeActiveNavigationItem(this.location);
    }

    ngOnInit(): void {
        jQuery(window).on('sn:resize', this.initSidebarScroll.bind(this));
        this.initSidebarScroll();
        setTimeout(() => {
            this.changeActiveNavigationItem(this.location);
        }, 200);

        this.router.events.subscribe((event) => {
            if (event instanceof NavigationEnd) {
                this.changeActiveNavigationItem(this.location);
            }
        });
    }

    ngOnDestroy() {
        this.gs_subscription.unsubscribe();
        this.user_subscription.unsubscribe();
    }
}
