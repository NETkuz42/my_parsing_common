from fabric import Connection


def get_images_links_from_server():
    host = '91.149.232.14'
    user = 'root'
    path_to_kay = r"D:\DISTRIB_LOCAL\PROGRAM\SSH\germany\private_kay_SSH"
    port = 22
    parent_images_dir = "/var/www/cyberdyne-systems/images"
    link_begin = "https://cyberdyne-systems.site/images"

    connect = Connection(host, user, port, connect_kwargs={'key_filename': path_to_kay})
    child_dir_list = connect.run(f'ls {parent_images_dir}').stdout.split()

    result_dict = {}
    for child_dir in child_dir_list:
        child_path = f"{parent_images_dir}/{child_dir}"
        files_names_list = connect.run(f"ls {child_path}").stdout.split()
        files_path_list = [fr"{link_begin}/{child_dir}/{name}"for name in files_names_list]
        result_dict.update({child_dir: files_path_list})

    print(result_dict)

    connect.close()

get_images_links_from_server()
