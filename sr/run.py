import func
import config

SESSION = func.update_session_id(
    config.FOREMAN_USER, config.FOREMAN_PASSWORD, config.FOREMAN_HOST)

# обновляется дефолтный глобальный пароль для операционных систем
func.change_global_root_pass(config.ADMIN_PASS)

architecture_ids = [func.get_id_name("x86_64", "architectures")]
location_ids = [func.get_id_name("moscow", "locations")]
organization_ids = [func.get_id_name("cloud.ru", "organizations")]
domain_ids = [func.get_id_name("cloud.ru", "domains")]
proxy_id = func.get_id_name(config.FOREMAN_PROXY_NAME, "smart_proxies")

# создаётся медиа
func.create_media(config.FOREMAN_PROXY_NAME, config.FOREMAN_PROXY_IP,
                  organization_ids=organization_ids, location_ids=location_ids)
id_media = [func.get_id_name(config.FOREMAN_PROXY_NAME, "media")]

# создаётся шаблоны
func.import_template("preseed_netplan_setup_demo")
func.import_template("preseed_kernel_options_autoinstall_demo")
func.import_template("Preseed default iPXE Autoinstall demo")
func.import_template("Preseed Autoinstall cloud-init user data demo")

# обновляется созданную по умолчанию операционку систему
ptable_ids = [func.get_id_name("Preseed default autoinstall", "ptables")]
provisioning_template_ids = []
provisioning_template_ids.append(func.get_id_name(
    "Preseed Autoinstall cloud-init user data demo", "provisioning_templates"))
provisioning_template_ids.append(func.get_id_name(
    "Preseed default iPXE Autoinstall demo", "provisioning_templates"))
provisioning_template_ids.append(func.get_id_name(
    "PXELinux chain iPXE", "provisioning_templates"))
provisioning_template_ids.append(func.get_id_name(
    "XenServer default finish", "provisioning_templates"))

# обновляется операционная система
id_os = 1
func.update_operatingsystems(
    id_os=id_os,
    id_media=id_media,
    provisioning_template_ids=provisioning_template_ids,
    ptable_ids=ptable_ids,
    architecture_ids=architecture_ids,
)

os_default_templates = []
for template_id in provisioning_template_ids:
    os_default_templates.append({"provisioning_template_id": template_id,
                                "template_kind_id": func.get_template_kind_id(template_id)})
for i in os_default_templates:
    func.update_operatingsystems_template(
        id_os=id_os,
        os_default_template=i
    )

# создаются сети
func.check_create_subnets(
    proxy_id=proxy_id,
    network=config.OS_NETWORK,
    network_type="os",
    netmask=config.OS_NETMASK,
    gateway=config.OS_GATAWAY,
    domain_ids=domain_ids,
    location_ids=location_ids,
    organization_ids=organization_ids,
    dns_primary=config.DNS1,
    dns_secondary=config.DNS2)
func.check_create_subnets(
    proxy_id=proxy_id,
    network=config.PXE_NETWORK,
    network_type="pxe",
    netmask=config.PXE_NETMASK,
    gateway=config.PXE_GATAWAY,
    domain_ids=domain_ids,
    location_ids=location_ids,
    organization_ids=organization_ids,
    dns_primary=config.DNS1,
    dns_secondary=config.DNS2)
subnet_os_id = func.get_id_name("%s-os" % config.OS_NETWORK, "subnets")
subnet_pxe_id = func.get_id_name("%s-pxe" % config.PXE_NETWORK, "subnets")

# создаётся хост
func.create_host(
    name=config.HOST_NAME,
    organization_id=organization_ids[0],
    location_id=location_ids[0],
    architecture_id=architecture_ids[0],
    operatingsystem_id=id_os,
    medium_id=id_media[0],
    ptable_id=ptable_ids[0],
    pxe_loader="PXELinux BIOS",
    domain_id=domain_ids[0],
    subnet_os_id=subnet_os_id,
    subnet_pxe_id=subnet_pxe_id,
    mac=config.MAC,
    os_ip=config.OS_IP)
