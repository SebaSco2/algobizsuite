FROM odoo:19

USER root

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

COPY etc /etc/odoo
COPY addons /mnt/extra-addons

CMD ["/usr/bin/python3", "/usr/lib/python3/dist-packages/odoo/odoo-bin", "--config", "/etc/odoo/odoo.conf", "--dev", "all"]