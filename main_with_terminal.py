from src.Classes.TerminalClasses.Terminal import Terminal

assets_path = 'C:\\Users\\rodri\\Documents\\Projetos\\cardpy_project\\assets\\'
terminal = Terminal(assets_path + 'terminal_tags.xml',
                    assets_path + 'acceptable_aids.xml',
                    assets_path + 'certificate_authority_public_keys.xml')

terminal.request_card(log_apdu=True)
terminal.build_candidate_list()
for candidate in terminal.candidate_list:
    print(candidate)
terminal.choose_application(1)
terminal.get_processing_options()
terminal.get_application_info()
terminal.run_offline_data_authentication()
