import { Component, markRaw,useRef, reactive, useChildSubEnv, xml } from "@odoo/owl";
import { registry } from "@web/core/registry";

class SidebarWrapper extends Component {
    static template = xml`
        <div class="sidebar-wrapper start-showing" t-if="props.subEnv.isActive" t-on-click="closeSidebar" t-ref="sidebarRef">
            <!-- Close button at the top-right corner -->
            <button class="close-sidebar" t-on-click="props.subEnv.close" aria-label="Close Sidebar">×</button>
            <!-- Render the subcomponent dynamically -->
            <t t-component="props.subComponent" t-props="props.subProps" />
        </div>
    `;
    static props = ["*"];
    setup() {
        // Pass down the sub-environment for child components
        useChildSubEnv({ sidebarData: this.props.subEnv });
        this.sidebarRef = useRef('sidebarRef')

    }
    closeSidebar(ev){
        var overlayItem = document.querySelector(".o-overlay-container .o-overlay-item");
        if(overlayItem){
            overlayItem.remove();
        }
    }
}
export const sidebarService = {
    dependencies: ["overlay"],
    start(env, { overlay }) {
        const stack = reactive([]);
        let nextId = 0;

        const add = (ComponentClass, props = {}, options = {}) => {
            const id = nextId++;
            const close = () => remove(id);
            const subEnv = reactive({
                id,
                close,
                isActive: true,
            });

            const remove = overlay.add(
                SidebarWrapper,
                {
                    subComponent: ComponentClass,
                    subProps: { ...props, close },
                    subEnv,
                },
                {
                    onRemove: () => {
                        stack.splice(stack.findIndex((item) => item.id === id), 1);
                        if (stack.length === 0) {
                            document.body.classList.remove("sidebar-open");
                        }
                        options.onClose?.();
                    },
                }
            );

            stack.push(subEnv);
            document.body.classList.add("sidebar-open");
            return remove;
        };

        return { add };
    },
};

registry.category("services").add("sidebar", sidebarService);
